from typing import Any

from agent.core.tools.base import BaseTool


class ToolRegistry:
    """Registry containing all available agent tools."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Register a tool."""

        if tool.name in self._tools:
            raise ValueError(
                f"Tool '{tool.name}' is already registered."
            )

        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        """Return a registered tool by name."""

        return self._tools.get(name)

    def all(self) -> list[BaseTool]:
        """Return all registered tools."""

        return list(self._tools.values())

    def schemas(self) -> list[dict[str, Any]]:
        """Return schemas for all registered tools."""

        return [
            tool.schema()
            for tool in self._tools.values()
        ]

    def execute(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> Any:
        """Execute a registered tool."""

        tool = self.get(name)

        if tool is None:
            raise ValueError(
                f"Unknown tool: {name}"
            )

        return tool.execute(**arguments)
