from pathlib import Path


class ToolContext:
    """Shared context available to agent tools."""

    def __init__(
        self,
        project_root: str | Path = ".",
    ) -> None:
        self.project_root = Path(
            project_root
        ).resolve()

        if not self.project_root.exists():
            raise FileNotFoundError(
                f"Project root does not exist: "
                f"{self.project_root}"
            )

        if not self.project_root.is_dir():
            raise NotADirectoryError(
                f"Project root is not a directory: "
                f"{self.project_root}"
            )

    def resolve_path(
        self,
        path: str | Path,
    ) -> Path:
        """Resolve a path and ensure it stays inside the project."""

        candidate = Path(path)

        if not candidate.is_absolute():
            candidate = self.project_root / candidate

        resolved = candidate.resolve()

        try:
            resolved.relative_to(
                self.project_root
            )
        except ValueError as exc:
            raise PermissionError(
                f"Path is outside the project root: "
                f"{path}"
            ) from exc

        return resolved
