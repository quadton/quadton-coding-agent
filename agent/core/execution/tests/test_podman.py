
import subprocess
from pathlib import Path

from agent.core.execution.podman import PodmanExecutionBackend


def test_podman_backend_name():
    assert PodmanExecutionBackend().name == "podman"


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


def test_podman_backend_starts_and_reuses_container(
    tmp_path: Path,
    monkeypatch,
):
    calls = []

    def fake_run(command, **kwargs):
        calls.append(command)

        class Result:
            returncode = 0
            stdout = "container-id"
            stderr = ""

        return Result()

    monkeypatch.setattr(
        "agent.core.execution.podman.subprocess.run",
        fake_run,
    )

    backend = PodmanExecutionBackend()

    first = backend.execute("echo first", cwd=str(tmp_path))
    second = backend.execute("echo second", cwd=str(tmp_path))

    assert first.success is True
    assert second.success is True
    assert len(calls) == 3

    start_command = calls[0]
    assert start_command[:2] == ["podman", "run"]
    assert "--detach" in start_command
    assert "--network" in start_command
    assert "none" in start_command
    assert f"{tmp_path}:/workspace" in start_command

    assert calls[1][:2] == ["podman", "exec"]
    assert calls[2][:2] == ["podman", "exec"]
    assert calls[1][3] == calls[2][3]

    backend.close()


def test_podman_backend_network_can_be_enabled(
    tmp_path: Path,
    monkeypatch,
):
    captured = []

    def fake_run(command, **kwargs):
        captured.append(command)

        class Result:
            returncode = 0
            stdout = "container-id"
            stderr = ""

        return Result()

    monkeypatch.setattr(
        "agent.core.execution.podman.subprocess.run",
        fake_run,
    )

    backend = PodmanExecutionBackend(network=True)
    result = backend.execute("echo test", cwd=str(tmp_path))

    assert result.success is True
    assert "--network" not in captured[0]

    backend.close()


def test_podman_backend_empty_command():
    result = PodmanExecutionBackend().execute("   ")

    assert result.success is False
    assert result.stderr == "Command must not be empty."


def test_podman_backend_invalid_timeout():
    result = PodmanExecutionBackend().execute(
        "echo test",
        timeout=0,
    )

    assert result.success is False
    assert result.stderr == "Timeout must be greater than 0 seconds."


def test_podman_backend_timeout(
    tmp_path: Path,
    monkeypatch,
):
    calls = 0

    def fake_run(command, **kwargs):
        nonlocal calls
        calls += 1

        if calls == 1:
            class StartResult:
                returncode = 0
                stdout = "container-id"
                stderr = ""

            return StartResult()

        raise subprocess.TimeoutExpired(
            command,
            kwargs.get("timeout"),
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
    assert result.stdout == "partial output"
    assert result.stderr == "partial error"

    backend.close()


def test_podman_backend_rejects_directory_outside_project(
    tmp_path: Path,
    monkeypatch,
):
    outside = tmp_path.parent / "outside-project"
    outside.mkdir()

    def fake_run(command, **kwargs):
        class Result:
            returncode = 0
            stdout = "container-id"
            stderr = ""

        return Result()

    monkeypatch.setattr(
        "agent.core.execution.podman.subprocess.run",
        fake_run,
    )

    backend = PodmanExecutionBackend()
    backend.execute("echo test", cwd=str(tmp_path))

    result = backend.execute("echo unsafe", cwd=str(outside))

    assert result.success is False
    assert "inside the mounted project" in result.stderr

    backend.close()


def test_podman_backend_unavailable(monkeypatch):
    def fake_run(command, **kwargs):
        class Result:
            returncode = 1
            stdout = ""
            stderr = "podman unavailable"

        return Result()

    monkeypatch.setattr(
        "agent.core.execution.podman.subprocess.run",
        fake_run,
    )

    assert PodmanExecutionBackend().is_available() is False
