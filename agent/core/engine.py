from pathlib import Path
from typing import Any

from agent.config import config
from agent.core.execution.base import ExecutionBackend
from agent.core.execution.factory import create_execution_backend
from agent.core.memory import Memory
from agent.core.providers.base import BaseProvider
from agent.core.providers.factory import create_provider
from agent.core.session import Session
from agent.core.tools.default import create_default_registry
from agent.core.tools.registry import ToolRegistry


class AgentEngine:
    """Core agentic engine for Quadton Coding Agent."""

    DEFAULT_MAX_ITERATIONS = 20

    def __init__(
        self,
        provider: BaseProvider | None = None,
        model: str | None = None,
        memory: Memory | None = None,
        session_id: int | None = None,
        tools: ToolRegistry | None = None,
        system_prompt: str | None = None,
        project_root: str | Path = ".",
        execution_backend: ExecutionBackend | None = None,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
    ):
        if max_iterations < 1:
            raise ValueError(
                "max_iterations must be greater than 0."
            )

        self.provider = provider or create_provider()

        if model:
            self.model = model
        elif self.provider.name == "openrouter":
            self.model = config.openrouter_model
        elif self.provider.name == "unorouter":
            self.model = config.unorouter_model
        else:
            raise ValueError(
                f"No model configuration exists for provider "
                f"'{self.provider.name}'."
            )

        if not self.model:
            raise ValueError(
                f"No model is configured for provider "
                f"'{self.provider.name}'. "
                "Set the appropriate model variable in your "
                ".env file or provide a model explicitly."
            )

        self.project_root = Path(
            project_root
        ).resolve()

        self.memory = memory or Memory()

        self.session = Session(
            self.memory,
            session_id=session_id,
        )

        self.system_prompt = system_prompt

        self.max_iterations = max_iterations

        self.messages: list[dict[str, Any]] = []

        if self.system_prompt:
            self.messages.append(
                {
                    "role": "system",
                    "content": self.system_prompt,
                }
            )

        self.messages.extend(
            self.session.get_messages()
        )

        self.execution_backend = (
            execution_backend
            or create_execution_backend()
        )

        self.tools = tools or create_default_registry(
            self.project_root,
            execution_backend=self.execution_backend,
        )

    def add_message(
        self,
        role: str,
        content: str,
        **extra: Any,
    ) -> None:
        """Add and persist a message."""

        message: dict[str, Any] = {
            "role": role,
            "content": content,
        }

        message.update(extra)

        self.messages.append(message)

        if role in {"user", "assistant"}:
            self.session.save_message(
                role,
                content or "",
            )

    def _execute_tool_call(
        self,
        tool_call: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a model-requested tool."""

        function = tool_call["function"]

        name = function["name"]
        arguments = function.get(
            "arguments",
            "{}",
        )

        try:
            import json

            parsed_arguments = json.loads(
                arguments
            )

        except json.JSONDecodeError as exc:
            return {
                "success": False,
                "error": (
                    f"Invalid tool arguments: {exc}"
                ),
            }

        try:
            result = self.tools.execute(
                name,
                parsed_arguments,
            )

            return {
                "success": True,
                "result": result,
            }

        except Exception as exc:
            return {
                "success": False,
                "error": str(exc),
            }

    def send_message(
        self,
        content: str,
    ) -> dict[str, Any]:
        """Run the agentic tool-calling loop."""

        self.add_message(
            "user",
            content,
        )

        iterations = 0

        while iterations < self.max_iterations:
            response = self.provider.send(
                self.messages,
                model=self.model,
                tools=self.tools.schemas(),
            )

            message = response.get(
                "message",
                {},
            )

            tool_calls = message.get(
                "tool_calls"
            ) or []

            if not tool_calls:
                assistant_content = (
                    message.get("content")
                    or ""
                )

                self.add_message(
                    "assistant",
                    assistant_content,
                )

                return response

            iterations += 1

            assistant_message = {
                "role": "assistant",
                "content": message.get(
                    "content"
                ),
                "tool_calls": tool_calls,
            }

            self.messages.append(
                assistant_message
            )

            for tool_call in tool_calls:
                result = self._execute_tool_call(
                    tool_call
                )

                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": self._serialize_result(
                            result
                        ),
                    }
                )

        limit_message = (
            "The agent reached its maximum execution "
            f"limit of {self.max_iterations} tool rounds "
            "without producing a final response."
        )

        self.add_message(
            "assistant",
            limit_message,
        )

        return {
            "message": {
                "role": "assistant",
                "content": limit_message,
            },
            "finish_reason": "max_iterations",
        }

    @staticmethod
    def _serialize_result(
        result: dict[str, Any],
    ) -> str:
        """Convert a tool result into JSON text."""

        import json

        return json.dumps(
            result,
            ensure_ascii=False,
        )

    def get_history(
        self,
    ) -> list[dict[str, Any]]:
        """Return the current conversation history."""

        return list(self.messages)

    def clear_history(self) -> None:
        """Clear conversation history while preserving system instructions."""

        self.messages.clear()

        if self.system_prompt:
            self.messages.append(
                {
                    "role": "system",
                    "content": self.system_prompt,
                }
            )
