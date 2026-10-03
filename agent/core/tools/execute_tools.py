from __future__ import annotations

from agent.core.execution.base import ExecutionBackend
from agent.core.execution.local import LocalExecutionBackend


def execute_command(
    command: str,
    *,
    timeout: int = 30,
    cwd: str | None = None,
    backend: ExecutionBackend | None = None,
) -> dict:
    """Execute a command using the configured execution backend."""

    execution_backend = backend or LocalExecutionBackend()

    result = execution_backend.execute(
        command,
        timeout=timeout,
        cwd=cwd,
    )

    return {
        "success": result.success,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.exit_code,
        "timed_out": result.timed_out,
        "metadata": result.metadata,
    }
