from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ExecutionResult:
    """Result returned by an execution backend."""

    success: bool
    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None
    timed_out: bool = False
    metadata: dict[str, Any] | None = None


class ExecutionBackend(ABC):
    """Abstract interface for executing commands."""

    name: str = "unknown"

    @abstractmethod
    def execute(
        self,
        command: str,
        *,
        timeout: int = 30,
        cwd: str | None = None,
    ) -> ExecutionResult:
        """Execute a command and return its result."""
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """Return whether the execution backend is available."""
        raise NotImplementedError

    def close(self) -> None:
        """Release backend resources."""
        return None
