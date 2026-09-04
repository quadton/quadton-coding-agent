from abc import ABC, abstractmethod
from typing import Any


class BaseProvider(ABC):
    """Base interface for all AI providers."""

    name: str = "unknown"

    @abstractmethod
    def send(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Send messages to the provider and return the response."""
        raise NotImplementedError

    @abstractmethod
    def stream(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str,
        tools: list[dict[str, Any]] | None = None,
    ):
        """Stream a response from the provider."""
        raise NotImplementedError
