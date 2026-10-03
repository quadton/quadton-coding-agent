from agent.core.execution.local import LocalExecutionBackend


def test_local_execution_success():
    backend = LocalExecutionBackend()

    result = backend.execute("printf 'hello'")

    assert result.success is True
    assert result.stdout == "hello"
    assert result.stderr == ""
    assert result.exit_code == 0
    assert result.timed_out is False


def test_local_execution_failure():
    backend = LocalExecutionBackend()

    result = backend.execute("sh -c 'printf \"error\" >&2; exit 2'")

    assert result.success is False
    assert result.stdout == ""
    assert result.stderr == "error"
    assert result.exit_code == 2
    assert result.timed_out is False


def test_local_execution_cwd(tmp_path):
    backend = LocalExecutionBackend()

    result = backend.execute("pwd", cwd=str(tmp_path))

    assert result.success is True
    assert result.stdout.strip() == str(tmp_path)
    assert result.exit_code == 0


def test_local_execution_timeout():
    backend = LocalExecutionBackend()

    result = backend.execute("sleep 2", timeout=1)

    assert result.success is False
    assert result.timed_out is True


def test_local_execution_empty_command():
    backend = LocalExecutionBackend()

    result = backend.execute("   ")

    assert result.success is False
    assert result.stderr == "Command must not be empty."


def test_local_execution_invalid_timeout():
    backend = LocalExecutionBackend()

    result = backend.execute("printf 'hello'", timeout=0)

    assert result.success is False
    assert result.stderr == "Timeout must be greater than 0 seconds."


def test_local_execution_available():
    backend = LocalExecutionBackend()

    assert backend.is_available() is True
