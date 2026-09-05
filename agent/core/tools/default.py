from agent.core.tools.file_tools import ListDirectoryTool
from agent.core.tools.registry import ToolRegistry


def create_default_registry() -> ToolRegistry:
    """Create the default tool registry."""

    registry = ToolRegistry()

    registry.register(
        ListDirectoryTool()
    )

    return registry
