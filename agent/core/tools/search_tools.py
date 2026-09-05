from pathlib import Path
from typing import Any

from agent.core.tools.base import BaseTool


DEFAULT_IGNORED_DIRECTORIES = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "ENV",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}


class SearchFilesTool(BaseTool):
    """Search project files for text."""

    name = "search_files"

    description = (
        "Search recursively through project text files for a "
        "text string. Returns matching file paths, line numbers, "
        "and matching lines. Use this to find symbols, functions, "
        "classes, imports, configuration values, or references."
    )

    def execute(
        self,
        query: str,
        path: str = ".",
        max_results: int = 100,
    ) -> dict[str, Any]:
        """Search files recursively for a text query."""

        if not query.strip():
            return {
                "success": False,
                "error": "Search query cannot be empty.",
            }

        if max_results < 1:
            return {
                "success": False,
                "error": "max_results must be at least 1.",
            }

        max_results = min(max_results, 500)

        try:
            search_root = self.context.resolve_path(path)

        except PermissionError as exc:
            return {
                "success": False,
                "error": str(exc),
            }

        if not search_root.exists():
            return {
                "success": False,
                "error": (
                    f"Search path does not exist: {path}"
                ),
            }

        if not search_root.is_dir():
            return {
                "success": False,
                "error": (
                    f"Search path is not a directory: {path}"
                ),
            }

        matches: list[dict[str, Any]] = []
        files_searched = 0
        truncated = False

        for file_path in self._iter_files(search_root):
            if len(matches) >= max_results:
                truncated = True
                break

            files_searched += 1

            try:
                with file_path.open(
                    "r",
                    encoding="utf-8",
                ) as file:
                    for line_number, line in enumerate(
                        file,
                        start=1,
                    ):
                        if query.casefold() in line.casefold():
                            relative_path = (
                                file_path.relative_to(
                                    self.context.project_root
                                )
                            )

                            matches.append(
                                {
                                    "file": str(
                                        relative_path
                                    ),
                                    "line": line_number,
                                    "text": line.rstrip(
                                        "\n\r"
                                    ),
                                }
                            )

                            if len(matches) >= max_results:
                                truncated = True
                                break

            except (
                UnicodeDecodeError,
                PermissionError,
                OSError,
            ):
                continue

        return {
            "success": True,
            "query": query,
            "path": str(search_root),
            "matches": matches,
            "match_count": len(matches),
            "files_searched": files_searched,
            "truncated": truncated,
        }

    def _iter_files(
        self,
        root: Path,
    ):
        """Yield searchable files recursively."""

        for current_root, directories, files in root.walk():
            directories[:] = [
                directory
                for directory in directories
                if directory
                not in DEFAULT_IGNORED_DIRECTORIES
            ]

            for filename in sorted(files):
                file_path = current_root / filename

                if self._should_skip_file(file_path):
                    continue

                yield file_path

    @staticmethod
    def _should_skip_file(
        path: Path,
    ) -> bool:
        """Return whether a file should be skipped."""

        if path.is_symlink():
            return True

        if path.name.startswith(".") and path.name not in {
            ".env",
            ".env.example",
        }:
            return True

        try:
            with path.open(
                "rb"
            ) as file:
                sample = file.read(8192)

        except OSError:
            return True

        return b"\x00" in sample

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
                        "query": {
                            "type": "string",
                            "description": (
                                "Text to search for. "
                                "The search is case-insensitive."
                            ),
                        },
                        "path": {
                            "type": "string",
                            "description": (
                                "Directory to search, relative "
                                "to the project root. Defaults "
                                "to '.'."
                            ),
                        },
                        "max_results": {
                            "type": "integer",
                            "description": (
                                "Maximum number of matching "
                                "lines to return. Defaults "
                                "to 100."
                            ),
                            "minimum": 1,
                            "maximum": 500,
                        },
                    },
                    "required": ["query"],
                },
            },
        }
