from typing import Any

from agent.config import config
from agent.core.memory import Memory
from agent.core.providers.base import BaseProvider
from agent.core.providers.openrouter_provider import OpenRouterProvider
from agent.core.session import Session


class AgentEngine:
    """Core conversation engine for Quadton Coding Agent."""

    def __init__(
        self,
        provider: BaseProvider | None = None,
        model: str | None = None,
        memory: Memory | None = None,
        session_id: int | None = None,
    ):
        self.provider = provider or OpenRouterProvider()

        self.model = model or config.openrouter_model

        if not self.model:
            raise ValueError(
                "No model is configured. "
                "Set OPENROUTER_MODEL in your .env file "
                "or provide a model explicitly."
            )

        self.memory = memory or Memory()

        self.session = Session(
            self.memory,
            session_id=session_id,
        )

        self.messages: list[dict[str, Any]] = (
            self.session.get_messages()
        )

    def add_message(
        self,
        role: str,
        content: str,
    ) -> None:
        """Add and persist a message."""

        message = {
            "role": role,
            "content": content,
        }

        self.messages.append(message)

        self.session.save_message(
            role,
            content,
        )

    def send_message(
        self,
        content: str,
    ) -> dict[str, Any]:
        """Send a user message and return the provider response."""

        self.add_message(
            "user",
            content,
        )

        try:
            response = self.provider.send(
                self.messages,
                model=self.model,
            )

        except Exception:
            self.messages.pop()
            raise

        message = response.get(
            "message",
            {},
        )

        assistant_message = {
            "role": message.get(
                "role",
                "assistant",
            ),
            "content": message.get(
                "content"
            ) or "",
        }

        self.messages.append(
            assistant_message
        )

        self.session.save_message(
            assistant_message["role"],
            assistant_message["content"],
        )

        return response

    def get_history(
        self,
    ) -> list[dict[str, Any]]:
        """Return the current conversation history."""

        return list(self.messages)

    def clear_history(self) -> None:
        """Clear the in-memory conversation."""

        self.messages.clear()
