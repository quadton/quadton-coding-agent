from __future__ import annotations

import subprocess

from .base import ExecutionBackend, ExecutionResult


class LocalExecutionBackend(ExecutionBackend):
    """Execute commands directly in the local environment."""

    name = "local"

    def execute(
        self,
        command: str,
        *,
        timeout: int = 30,
        cwd: str | None = None,
    ) -> ExecutionResult:
        """Execute a shell command locally."""

        if not command.strip():
            return ExecutionResult(
                success=False,
                stderr="Command must not be empty.",
                exit_code=None,
            )

        if timeout <= 0:
            return ExecutionResult(
                success=False,
                stderr="Timeout must be greater than 0 seconds.",
                exit_code=None,
            )

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            return ExecutionResult(
                success=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
            )

        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""

            if isinstance(stdout, bytes):
                stdout = stdout.decode(errors="replace")

            if isinstance(stderr, bytes):
                stderr = stderr.decode(errors="replace")

            return ExecutionResult(
                success=False,
                stdout=stdout,
                stderr=stderr,
                exit_code=None,
                timed_out=True,
            )

        except OSError as exc:
            return ExecutionResult(
                success=False,
                stderr=str(exc),
                exit_code=None,
            )

    def is_available(self) -> bool:
        """Return whether local command execution is available."""

        return True
