from __future__ import annotations

import subprocess

from .base import ExecutionBackend, ExecutionResult


class PodmanExecutionBackend(ExecutionBackend):
    """Execute commands inside disposable Podman containers."""

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

    def execute(
        self,
        command: str,
        *,
        timeout: int = 30,
        cwd: str | None = None,
    ) -> ExecutionResult:
        """Execute a command inside a disposable Podman container."""

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

        project_root = cwd or "."

        container_cwd = self.DEFAULT_WORKDIR

        if cwd and cwd != project_root:
            container_cwd = self.DEFAULT_WORKDIR

        cmd = [
            "podman",
            "run",
            "--rm",
            "--volume",
            f"{project_root}:{self.DEFAULT_WORKDIR}",
            "--workdir",
            container_cwd,
        ]

        if not self.network:
            cmd.extend(
                [
                    "--network",
                    "none",
                ]
            )

        cmd.extend(
            [
                self.image,
                "sh",
                "-c",
                command,
            ]
        )

        try:
            result = subprocess.run(
                cmd,
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
        """Return whether Podman is installed and usable."""

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
