from agent.core.execution.base import ExecutionResult
from agent.core.execution.codesandbox import CodeSandboxBackend


def fake_runner(**kwargs):
    assert kwargs["command"] == "python -c \"print('hello')\""
    assert kwargs["timeout"] == 10
    assert kwargs["cwd"] == "/workspace"

    return {
        "success": True,
        "stdout": "hello\n",
        "stderr": "",
        "exit_code": 0,
        "timed_out": False,
        "sandbox_id": "sandbox-123",
    }


def test_codesandbox_backend_is_named():
    backend = CodeSandboxBackend(
        api_key="test-key",
        runner=fake_runner,
    )

    assert backend.name == "codesandbox"


def test_codesandbox_backend_executes_and_persists_sandbox_id():
    backend = CodeSandboxBackend(
        api_key="test-key",
        runner=fake_runner,
    )

    result = backend.execute(
        "python -c \"print('hello')\"",
        timeout=10,
        cwd="/workspace",
    )

    assert isinstance(result, ExecutionResult)
    assert result.success is True
    assert result.stdout == "hello\n"
    assert result.exit_code == 0

    assert result.metadata == {
        "backend": "codesandbox",
        "sandbox_id": "sandbox-123",
    }

    assert backend.sandbox_id == "sandbox-123"


def test_codesandbox_backend_rejects_empty_command():
    backend = CodeSandboxBackend(
        api_key="test-key",
        runner=fake_runner,
    )

    result = backend.execute("   ")

    assert result.success is False
    assert "empty" in result.stderr.lower()


def test_codesandbox_backend_rejects_invalid_timeout():
    backend = CodeSandboxBackend(
        api_key="test-key",
        runner=fake_runner,
    )

    result = backend.execute(
        "echo hello",
        timeout=0,
    )

    assert result.success is False
    assert "greater than 0" in result.stderr


def test_codesandbox_backend_rejects_execution_after_close():
    backend = CodeSandboxBackend(
        api_key="test-key",
        runner=fake_runner,
    )

    backend.close()

    result = backend.execute("echo hello")

    assert result.success is False
    assert "closed" in result.stderr.lower()


def test_codesandbox_backend_reports_missing_configuration():
    backend = CodeSandboxBackend(
        api_key=None,
        node_binary=None,
    )

    result = backend.execute("echo hello")

    assert result.success is False
    assert "CSB_API_KEY" in result.stderr
