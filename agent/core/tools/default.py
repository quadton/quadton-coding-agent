from pathlib import Path

from agent.core.tools.context import ToolContext
from agent.core.tools.file_tools import ListDirectoryTool
from agent.core.tools.read_tools import ReadFileTool
from agent.core.tools.registry import ToolRegistry
from agent.core.tools.search_tools import SearchFilesTool
from agent.core.tools.write_tools import WriteFileTool


def create_default_registry(
    project_root: str | Path = ".",
) -> ToolRegistry:
    """Create the default tool registry."""

    context = ToolContext(
        project_root
    )

    registry = ToolRegistry()

    registry.register(
        ListDirectoryTool(context)
    )

    registry.register(
        ReadFileTool(context)
    )

    registry.register(
        SearchFilesTool(context)
    )

    registry.register(
        WriteFileTool(context)
    )

    return registry
