from __future__ import annotations

from typing import Any

from agent.core.execution.base import ExecutionBackend
from agent.core.execution.local import LocalExecutionBackend
from agent.core.tools.base import BaseTool


class ExecuteCommandTool(BaseTool):
    """Execute a shell command through the configured execution backend."""

    name = "execute_command"

    description = (
        "Execute a shell command in the project environment. "
        "Use this to run programs, inspect the environment, "
        "run tests, install dependencies, or perform other "
        "command-line operations."
    )

    DEFAULT_TIMEOUT = 30
    MAX_TIMEOUT = 300

    def __init__(
        self,
        context,
        backend: ExecutionBackend | None = None,
    ) -> None:
        super().__init__(context)
        self.backend = backend or LocalExecutionBackend()

    def execute(
        self,
        command: str,
        timeout: int = DEFAULT_TIMEOUT,
        cwd: str | None = None,
    ) -> dict[str, Any]:
        """Execute a shell command."""

        if not command.strip():
            return {
                "success": False,
                "error": "Command must not be empty.",
            }

        if timeout < 1:
            return {
                "success": False,
                "error": "Timeout must be greater than 0 seconds.",
            }

        if timeout > self.MAX_TIMEOUT:
            return {
                "success": False,
                "error": (
                    f"Timeout cannot exceed {self.MAX_TIMEOUT} seconds."
                ),
            }

        execution_cwd = cwd

        if execution_cwd is None:
            execution_cwd = str(self.context.project_root)

        try:
            result = self.backend.execute(
                command,
                timeout=timeout,
                cwd=execution_cwd,
            )

        except Exception as exc:
            return {
                "success": False,
                "error": f"Execution backend failed: {exc}",
            }

        return {
            "success": result.success,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.exit_code,
            "timed_out": result.timed_out,
            "metadata": result.metadata,
        }

    def schema(self) -> dict[str, Any]:
        """Return the OpenAI-compatible tool schema."""

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": (
                                "Shell command to execute."
                            ),
                        },
                        "timeout": {
                            "type": "integer",
                            "description": (
                                "Maximum execution time in seconds. "
                                "Defaults to 30."
                            ),
                            "minimum": 1,
                            "maximum": self.MAX_TIMEOUT,
                        },
                        "cwd": {
                            "type": ["string", "null"],
                            "description": (
                                "Optional working directory. "
                                "Defaults to the project root."
                            ),
                        },
                    },
                    "required": ["command"],
                },
            },
        }
