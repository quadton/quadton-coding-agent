import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable

from .base import ExecutionBackend, ExecutionResult


Runner = Callable[..., dict[str, Any]]


class CodeSandboxBackend(ExecutionBackend):
    """Execution backend backed by the CodeSandbox SDK.

    The Python agent talks to the official CodeSandbox TypeScript SDK through
    a small Node.js bridge. A sandbox ID is retained by this backend so
    multiple commands share the same persistent sandbox.
    """

    name = "codesandbox"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        sandbox_id: str | None = None,
        bridge_path: str | Path | None = None,
        node_binary: str | None = None,
        runner: Runner | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else os.getenv("CSB_API_KEY")
        self.sandbox_id = sandbox_id or os.getenv("QUADTON_CODESANDBOX_ID")
        self.node_binary = node_binary or shutil.which("node")
        self.bridge_path = Path(bridge_path) if bridge_path else (
            Path(__file__).with_name("codesandbox_bridge.mjs")
        )
        self._runner = runner
        self._closed = False

    def is_available(self) -> bool:
        """Return whether the local prerequisites for CodeSandbox are present."""
        sdk_path = (
            Path(__file__).resolve().parents[3]
            / "node_modules"
            / "@codesandbox"
            / "sdk"
        )
        return bool(
            self.api_key
            and self.node_binary
            and self.bridge_path.is_file()
            and sdk_path.is_dir()
        )

    def execute(
        self,
        command: str,
        *,
        timeout: int = 30,
        cwd: str | None = None,
    ) -> ExecutionResult:
        """Execute a command inside the persistent CodeSandbox VM."""
        if self._closed:
            return ExecutionResult(
                success=False,
                stderr="CodeSandbox backend is closed.",
            )

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

        if not self.is_available() and self._runner is None:
            return ExecutionResult(
                success=False,
                stderr=(
                    "CodeSandbox backend is not available. "
                    "Set CSB_API_KEY and install Node.js with the "
                    "@codesandbox/sdk package."
                ),
            )

        try:
            if self._runner is not None:
                payload = self._runner(
                    command=command,
                    timeout=timeout,
                    cwd=cwd,
                    sandbox_id=self.sandbox_id,
                    api_key=self.api_key,
                )
            else:
                payload = self._run_bridge(
                    command=command,
                    timeout=timeout,
                    cwd=cwd,
                )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                stderr="CodeSandbox bridge timed out.",
                timed_out=True,
            )
        except (OSError, ValueError) as exc:
            return ExecutionResult(
                success=False,
                stderr=str(exc),
            )

        sandbox_id = payload.get("sandbox_id")
        if sandbox_id:
            self.sandbox_id = str(sandbox_id)

        return ExecutionResult(
            success=bool(payload.get("success", False)),
            stdout=str(payload.get("stdout", "")),
            stderr=str(payload.get("stderr", "")),
            exit_code=payload.get("exit_code"),
            timed_out=bool(payload.get("timed_out", False)),
            metadata={
                "backend": self.name,
                "sandbox_id": self.sandbox_id,
            },
        )

    def _run_bridge(
        self,
        *,
        command: str,
        timeout: int,
        cwd: str | None,
    ) -> dict[str, Any]:
        env = os.environ.copy()
        env["CSB_API_KEY"] = self.api_key or ""

        if self.sandbox_id:
            env["QUADTON_CODESANDBOX_ID"] = self.sandbox_id

        request = json.dumps(
            {
                "command": command,
                "timeout": timeout,
                "cwd": cwd,
                "sandbox_id": self.sandbox_id,
            }
        )

        completed = subprocess.run(
            [self.node_binary, str(self.bridge_path)],
            input=request,
            text=True,
            capture_output=True,
            timeout=timeout + 10,
            env=env,
            check=False,
        )

        if completed.returncode != 0:
            message = completed.stderr.strip() or "CodeSandbox bridge failed."
            raise OSError(message)

        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "CodeSandbox bridge returned invalid JSON."
            ) from exc

        if not isinstance(payload, dict):
            raise ValueError("CodeSandbox bridge returned a non-object result.")

        return payload

    def close(self) -> None:
        """Mark this backend closed.

        The sandbox itself is intentionally not shut down here. Lifecycle
        management will be added separately so the agent can hibernate or
        resume persistent environments without destroying them.
        """
        self._closed = True
