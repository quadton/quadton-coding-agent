from pathlib import Path
from typing import Any

from agent.core.tools.base import BaseTool


class ReadFileTool(BaseTool):
    """Read the contents of a text file."""

    name = "read_file"

    description = (
        "Read the contents of a text file. "
        "Use this to inspect source code, configuration, "
        "documentation, or other text files."
    )

    def execute(
        self,
        path: str,
    ) -> dict[str, Any]:
        """Read a text file."""

        if not path.strip():
            return {
                "success": False,
                "error": "File path cannot be empty.",
            }

        target = Path(path).resolve()

        if not target.exists():
            return {
                "success": False,
                "error": f"File does not exist: {path}",
            }

        if not target.is_file():
            return {
                "success": False,
                "error": f"Path is not a file: {path}",
            }

        try:
            content = target.read_text(
                encoding="utf-8"
            )

        except UnicodeDecodeError:
            return {
                "success": False,
                "error": (
                    f"File is not valid UTF-8 text: {path}"
                ),
            }

        except OSError as exc:
            return {
                "success": False,
                "error": (
                    f"Failed to read file: {exc}"
                ),
            }

        return {
            "success": True,
            "path": str(target),
            "content": content,
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
                                "Path to the text file "
                                "that should be read."
                            ),
                        }
                    },
                    "required": ["path"],
                },
            },
        }
