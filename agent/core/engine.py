from typing import Any

from agent.config import config
from agent.core.providers.base import BaseProvider
from agent.core.providers.openrouter_provider import OpenRouterProvider


class AgentEngine:
    """Core conversation engine for Quadton Coding Agent."""

    def __init__(
        self,
        provider: BaseProvider | None = None,
        model: str | None = None,
    ):
        self.provider = provider or OpenRouterProvider()

        self.model = model or config.openrouter_model

        if not self.model:
            raise ValueError(
                "No model is configured. "
                "Set OPENROUTER_MODEL in your .env file "
                "or provide a model explicitly."
            )

        self.messages: list[dict[str, Any]] = []

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the current conversation."""
        self.messages.append(
            {
                "role": role,
                "content": content,
            }
        )

    def send_message(self, content: str) -> dict[str, Any]:
        """Send a user message and return the provider response."""

        self.add_message("user", content)

        try:
            response = self.provider.send(
                self.messages,
                model=self.model,
            )
        except Exception:
            # Remove the user message if the request failed.
            self.messages.pop()
            raise

        message = response.get("message", {})

        assistant_message = {
            "role": message.get("role", "assistant"),
            "content": message.get("content") or "",
        }

        self.messages.append(assistant_message)

        return response

    def get_history(self) -> list[dict[str, Any]]:
        """Return the current conversation history."""
        return list(self.messages)

    def clear_history(self) -> None:
        """Clear the current conversation."""
        self.messages.clear()
