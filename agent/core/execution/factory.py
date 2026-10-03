from __future__ import annotations

from agent.config import config

from .base import ExecutionBackend
from .local import LocalExecutionBackend
from .podman import PodmanExecutionBackend


def create_execution_backend() -> ExecutionBackend:
    """Create the execution backend configured for Quadton."""

    backend_name = config.execution_backend

    if backend_name == "local":
        return LocalExecutionBackend()

    if backend_name == "podman":
        return PodmanExecutionBackend()

    raise ValueError(
        f"Unknown execution backend '{backend_name}'. "
        "Supported backends: local, podman."
    )
