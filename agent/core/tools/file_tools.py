from pathlib import Path
from typing import Any

from agent.core.tools.base import BaseTool


class ListDirectoryTool(BaseTool):
    """List files and directories."""

    name = "list_directory"

    description = (
        "List the files and directories inside a directory."
    )

    def execute(
        self,
        path: str = ".",
    ) -> dict[str, Any]:
        """List directory contents."""

        target = Path(path).resolve()

        if not target.exists():
            return {
                "success": False,
                "error": f"Path does not exist: {path}",
            }

        if not target.is_dir():
            return {
                "success": False,
                "error": f"Path is not a directory: {path}",
            }

        entries = []

        for entry in sorted(
            target.iterdir(),
            key=lambda item: (
                not item.is_dir(),
                item.name.lower(),
            ),
        ):
            entries.append(
                {
                    "name": entry.name,
                    "type": (
                        "directory"
                        if entry.is_dir()
                        else "file"
                    ),
                }
            )

        return {
            "success": True,
            "path": str(target),
            "entries": entries,
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
                        "path": {
                            "type": "string",
                            "description": (
                                "Directory to inspect. "
                                "Defaults to the current "
                                "working directory."
                            ),
                        }
                    },
                    "required": [],
                },
            },
        }
