from abc import ABC, abstractmethod
from typing import Any

from agent.core.tools.context import ToolContext


class BaseTool(ABC):
    """Base interface for all agent tools."""

    name: str = "unknown"
    description: str = ""

    def __init__(
        self,
        context: ToolContext,
    ) -> None:
        self.context = context

    @abstractmethod
    def execute(
        self,
        **kwargs: Any,
    ) -> Any:
        """Execute the tool."""
        raise NotImplementedError

    @abstractmethod
    def schema(self) -> dict[str, Any]:
        """Return the tool schema for the AI provider."""
        raise NotImplementedError
