from agent.core.tools.file_tools import ListDirectoryTool
from agent.core.tools.read_tools import ReadFileTool
from agent.core.tools.registry import ToolRegistry


def create_default_registry() -> ToolRegistry:
    """Create the default tool registry."""

    registry = ToolRegistry()

    registry.register(
        ListDirectoryTool()
    )

    registry.register(
        ReadFileTool()
    )

    return registry
