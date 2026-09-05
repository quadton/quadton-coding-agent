from typing import Any

from agent.core.tools.base import BaseTool


class WriteFileTool(BaseTool):
    """Create or overwrite a text file inside the project."""

    name = "write_file"

    description = (
        "Create or overwrite a UTF-8 text file inside the project. "
        "Use this when creating new files or intentionally replacing "
        "the complete contents of an existing file."
    )

    MAX_FILE_SIZE = 1_000_000

    def execute(
        self,
        path: str,
        content: str,
    ) -> dict[str, Any]:
        """Write text content to a project file."""

        if not path.strip():
            return {
                "success": False,
                "error": "File path cannot be empty.",
            }

        if not isinstance(content, str):
            return {
                "success": False,
                "error": "File content must be a string.",
            }

        content_size = len(
            content.encode("utf-8")
        )

        if content_size > self.MAX_FILE_SIZE:
            return {
                "success": False,
                "error": (
                    "File content exceeds the maximum "
                    f"size of {self.MAX_FILE_SIZE} bytes."
                ),
            }

        try:
            target = self.context.resolve_path(path)

        except PermissionError as exc:
            return {
                "success": False,
                "error": str(exc),
            }

        if target.exists() and not target.is_file():
            return {
                "success": False,
                "error": (
                    f"Path is not a file: {path}"
                ),
            }

        existed = target.exists()

        try:
            target.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            target.write_text(
                content,
                encoding="utf-8",
            )

        except OSError as exc:
            return {
                "success": False,
                "error": (
                    f"Failed to write file: {exc}"
                ),
            }

        return {
            "success": True,
            "path": str(target),
            "created": not existed,
            "overwritten": existed,
            "bytes_written": content_size,
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
                                "Path to the file, relative "
                                "to the project root."
                            ),
                        },
                        "content": {
                            "type": "string",
                            "description": (
                                "Complete UTF-8 text content "
                                "to write to the file."
                            ),
                        },
                    },
                    "required": [
                        "path",
                        "content",
                    ],
                },
            },
        }
