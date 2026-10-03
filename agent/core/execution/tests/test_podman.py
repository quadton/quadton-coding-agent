import subprocess
from pathlib import Path

from agent.core.execution.podman import PodmanExecutionBackend


def test_podman_backend_name():
    backend = PodmanExecutionBackend()

    assert backend.name == "podman"


def test_podman_backend_defaults():
    backend = PodmanExecutionBackend()

    assert backend.image == "python:3.12-slim"
    assert backend.network is False


def test_podman_backend_custom_options():
    backend = PodmanExecutionBackend(
        image="python:3.11-slim",
        network=True,
    )

    assert backend.image == "python:3.11-slim"
    assert backend.network is True


def test_podman_backend_builds_isolated_command(
    tmp_path: Path,
    monkeypatch,
):
    captured = {}

    def fake_run(
        command,
        *,
        capture_output,
        text,
        timeout,
    ):
        captured["command"] = command
        captured["timeout"] = timeout

        class Result:
            returncode = 0
            stdout = "hello"
            stderr = ""

        return Result()

    monkeypatch.setattr(
        "agent.core.execution.podman.subprocess.run",
        fake_run,
    )

    backend = PodmanExecutionBackend()

    result = backend.execute(
        "printf 'hello'",
        timeout=45,
        cwd=str(tmp_path),
    )

    command = captured["command"]

    assert result.success is True
    assert result.stdout == "hello"
    assert result.exit_code == 0
    assert captured["timeout"] == 45

    assert command[:3] == [
        "podman",
        "run",
        "--rm",
    ]

    assert "--network" in command
    assert "none" in command
    assert "--volume" in command
    assert f"{tmp_path}:/workspace" in command
    assert "--workdir" in command
    assert "/workspace" in command
    assert "python:3.12-slim" in command
    assert "sh" in command
    assert "-c" in command
    assert "printf 'hello'" in command


def test_podman_backend_network_can_be_enabled(
    tmp_path: Path,
    monkeypatch,
):
    captured = {}

    def fake_run(
        command,
        *,
        capture_output,
        text,
        timeout,
    ):
        captured["command"] = command

        class Result:
            returncode = 0
            stdout = ""
            stderr = ""

        return Result()

    monkeypatch.setattr(
        "agent.core.execution.podman.subprocess.run",
        fake_run,
    )

    backend = PodmanExecutionBackend(
        network=True,
    )

    result = backend.execute(
        "echo test",
        cwd=str(tmp_path),
    )

    assert result.success is True
    assert "--network" not in captured["command"]


def test_podman_backend_empty_command():
    backend = PodmanExecutionBackend()

    result = backend.execute("   ")

    assert result.success is False
    assert result.stderr == "Command must not be empty."


def test_podman_backend_invalid_timeout():
    backend = PodmanExecutionBackend()

    result = backend.execute(
        "echo test",
        timeout=0,
    )

    assert result.success is False
    assert result.stderr == "Timeout must be greater than 0 seconds."


def test_podman_backend_timeout(
    tmp_path: Path,
    monkeypatch,
):
    def fake_run(
        command,
        *,
        capture_output,
        text,
        timeout,
    ):
        raise subprocess.TimeoutExpired(
            command,
            timeout,
            output="partial output",
            stderr="partial error",
        )

    monkeypatch.setattr(
        "agent.core.execution.podman.subprocess.run",
        fake_run,
    )

    backend = PodmanExecutionBackend()

    result = backend.execute(
        "sleep 60",
        timeout=1,
        cwd=str(tmp_path),
    )

    assert result.success is False
    assert result.timed_out is True
    assert result.exit_code is None
    assert result.stdout == "partial output"
    assert result.stderr == "partial error"


def test_podman_backend_unavailable(
    monkeypatch,
):
    def fake_run(
        command,
        *,
        capture_output,
        text,
        timeout,
    ):
        class Result:
            returncode = 1
            stdout = ""
            stderr = "podman unavailable"

        return Result()

    monkeypatch.setattr(
        "agent.core.execution.podman.subprocess.run",
        fake_run,
    )

    backend = PodmanExecutionBackend()

    assert backend.is_available() is False
