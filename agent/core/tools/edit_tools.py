from typing import Any

from agent.core.tools.base import BaseTool


class EditFileTool(BaseTool):
    """Apply targeted text replacements to a file."""

    name = "edit_file"

    description = (
        "Edit a UTF-8 text file inside the project by replacing exact "
        "text. Use this for targeted modifications instead of rewriting "
        "the entire file. The replacement count must match the expected "
        "number when provided."
    )

    MAX_FILE_SIZE = 1_000_000

    def execute(
        self,
        path: str,
        old_text: str,
        new_text: str,
        expected_occurrences: int = 1,
    ) -> dict[str, Any]:
        """Replace exact text inside a project file."""

        if not path.strip():
            return {
                "success": False,
                "error": "File path cannot be empty.",
            }

        if not old_text:
            return {
                "success": False,
                "error": "old_text cannot be empty.",
            }

        if expected_occurrences < 1:
            return {
                "success": False,
                "error": (
                    "expected_occurrences must be at least 1."
                ),
            }

        try:
            target = self.context.resolve_path(path)

        except PermissionError as exc:
            return {
                "success": False,
                "error": str(exc),
            }

        if not target.exists():
            return {
                "success": False,
                "error": (
                    f"File does not exist: {path}"
                ),
            }

        if not target.is_file():
            return {
                "success": False,
                "error": (
                    f"Path is not a file: {path}"
                ),
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

        current_occurrences = content.count(old_text)

        if current_occurrences == 0:
            return {
                "success": False,
                "error": (
                    "The specified old_text was not found "
                    f"in {path}."
                ),
            }

        if current_occurrences != expected_occurrences:
            return {
                "success": False,
                "error": (
                    "Occurrence count mismatch. "
                    f"Expected {expected_occurrences}, "
                    f"but found {current_occurrences}."
                ),
                "found_occurrences": current_occurrences,
            }

        updated_content = content.replace(
            old_text,
            new_text,
        )

        updated_size = len(
            updated_content.encode("utf-8")
        )

        if updated_size > self.MAX_FILE_SIZE:
            return {
                "success": False,
                "error": (
                    "Updated file exceeds the maximum "
                    f"size of {self.MAX_FILE_SIZE} bytes."
                ),
            }

        try:
            target.write_text(
                updated_content,
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
            "replacements": current_occurrences,
            "bytes_written": updated_size,
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
                        "old_text": {
                            "type": "string",
                            "description": (
                                "Exact text that should be replaced."
                            ),
                        },
                        "new_text": {
                            "type": "string",
                            "description": (
                                "Text that should replace old_text."
                            ),
                        },
                        "expected_occurrences": {
                            "type": "integer",
                            "description": (
                                "Expected number of exact matches. "
                                "Defaults to 1."
                            ),
                            "minimum": 1,
                        },
                    },
                    "required": [
                        "path",
                        "old_text",
                        "new_text",
                    ],
                },
            },
        }
