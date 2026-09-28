from agent.core.execution.base import (
    ExecutionBackend,
    ExecutionResult,
)


def test_execution_result_defaults():
    result = ExecutionResult(success=True)

    assert result.success is True
    assert result.stdout == ""
    assert result.stderr == ""
    assert result.exit_code is None
    assert result.timed_out is False
    assert result.metadata is None


def test_execution_result_with_output():
    result = ExecutionResult(
        success=True,
        stdout="hello",
        stderr="",
        exit_code=0,
    )

    assert result.success is True
    assert result.stdout == "hello"
    assert result.exit_code == 0


def test_execution_result_failure():
    result = ExecutionResult(
        success=False,
        stdout="",
        stderr="command failed",
        exit_code=1,
    )

    assert result.success is False
    assert result.stderr == "command failed"
    assert result.exit_code == 1


def test_execution_backend_is_abstract():
    assert ExecutionBackend.__abstractmethods__ == {
        "execute",
        "is_available",
    }
