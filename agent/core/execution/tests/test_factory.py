import pytest

from agent.core.execution.factory import create_execution_backend
from agent.core.execution.local import LocalExecutionBackend
from agent.core.execution.podman import PodmanExecutionBackend


def test_factory_creates_local_backend(monkeypatch):
    monkeypatch.setattr(
        "agent.core.execution.factory.config.execution_backend",
        "local",
    )

    backend = create_execution_backend()

    assert isinstance(
        backend,
        LocalExecutionBackend,
    )


def test_factory_creates_podman_backend(monkeypatch):
    monkeypatch.setattr(
        "agent.core.execution.factory.config.execution_backend",
        "podman",
    )

    backend = create_execution_backend()

    assert isinstance(
        backend,
        PodmanExecutionBackend,
    )


def test_factory_rejects_unknown_backend(monkeypatch):
    monkeypatch.setattr(
        "agent.core.execution.factory.config.execution_backend",
        "unknown",
    )

    with pytest.raises(
        ValueError,
        match="Unknown execution backend",
    ):
        create_execution_backend()
