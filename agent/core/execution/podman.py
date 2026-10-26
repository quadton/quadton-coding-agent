
from __future__ import annotations

import subprocess
import uuid
from pathlib import Path

from .base import ExecutionBackend, ExecutionResult


class PodmanExecutionBackend(ExecutionBackend):
    """Run commands in one isolated container per agent task."""

    name = "podman"

    DEFAULT_IMAGE = "python:3.12-slim"
    DEFAULT_WORKDIR = "/workspace"

    def __init__(
        self,
        image: str = DEFAULT_IMAGE,
        network: bool = False,
    ) -> None:
        self.image = image
        self.network = network
        self._container_name: str | None = None
        self._project_root: Path | None = None

    def _start_container(self, project_root: Path) -> ExecutionResult | None:
        """Start a reusable container with the project mounted."""

        self._project_root = project_root
        self._container_name = f"quadton-{uuid.uuid4().hex[:12]}"

        command = [
            "podman",
            "run",
            "--detach",
            "--name",
            self._container_name,
            "--volume",
            f"{project_root}:{self.DEFAULT_WORKDIR}",
            "--workdir",
            self.DEFAULT_WORKDIR,
        ]

        if not self.network:
            command.extend(["--network", "none"])

        command.extend([
            self.image,
            "sh",
            "-c",
            "while true; do sleep 3600; done",
        ])

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            self._container_name = None
            self._project_root = None
            return ExecutionResult(
                success=False,
                stderr=f"Failed to start Podman container: {exc}",
            )

        if result.returncode != 0:
            self._container_name = None
            self._project_root = None
            return ExecutionResult(
                success=False,
                stdout=result.stdout,
                stderr=result.stderr or "Podman failed to start the container.",
                exit_code=result.returncode,
            )

        return None

    def execute(
        self,
        command: str,
        *,
        timeout: int = 30,
        cwd: str | None = None,
    ) -> ExecutionResult:
        """Execute a command in the task's reusable container."""

        if not command.strip():
            return ExecutionResult(
                success=False,
                stderr="Command must not be empty.",
            )

        if timeout <= 0:
            return ExecutionResult(
                success=False,
                stderr="Timeout must be greater than 0 seconds.",
            )

        try:
            requested_cwd = Path(cwd or ".").resolve()

            if self._project_root is None:
                startup_error = self._start_container(requested_cwd)
                if startup_error is not None:
                    return startup_error

            assert self._project_root is not None
            assert self._container_name is not None

            try:
                relative_cwd = requested_cwd.relative_to(
                    self._project_root
                )
            except ValueError:
                return ExecutionResult(
                    success=False,
                    stderr=(
                        "Working directory must be inside the "
                        "mounted project directory."
                    ),
                )

            container_cwd = str(
                Path(self.DEFAULT_WORKDIR) / relative_cwd
            )

            result = subprocess.run(
                [
                    "podman",
                    "exec",
                    "--workdir",
                    container_cwd,
                    self._container_name,
                    "sh",
                    "-c",
                    command,
                ],
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
                timed_out=True,
            )

        except OSError as exc:
            return ExecutionResult(
                success=False,
                stderr=str(exc),
            )

    def close(self) -> None:
        """Stop and remove the task container."""

        container_name = self._container_name

        self._container_name = None
        self._project_root = None

        if container_name is None:
            return

        try:
            subprocess.run(
                ["podman", "rm", "--force", container_name],
                capture_output=True,
                text=True,
                timeout=15,
            )
        except (OSError, subprocess.TimeoutExpired):
            pass

    def is_available(self) -> bool:
        """Check whether Podman is installed and usable."""

        try:
            result = subprocess.run(
                ["podman", "info"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            return False
