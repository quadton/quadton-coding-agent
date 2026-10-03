from pathlib import Path

from agent.core.execution.base import ExecutionBackend, ExecutionResult
from agent.core.tools.context import ToolContext
from agent.core.tools.execute_tools import ExecuteCommandTool


class FakeExecutionBackend(ExecutionBackend):
    """Fake backend for testing the command tool."""

    name = "fake"

    def __init__(self) -> None:
        self.last_command: str | None = None
        self.last_timeout: int | None = None
        self.last_cwd: str | None = None

    def execute(
        self,
        command: str,
        *,
        timeout: int = 30,
        cwd: str | None = None,
    ) -> ExecutionResult:
        self.last_command = command
        self.last_timeout = timeout
        self.last_cwd = cwd

        return ExecutionResult(
            success=True,
            stdout="fake output",
            stderr="",
            exit_code=0,
        )

    def is_available(self) -> bool:
        return True


def test_execute_command_success(tmp_path: Path):
    backend = FakeExecutionBackend()
    context = ToolContext(tmp_path)
    tool = ExecuteCommandTool(context, backend=backend)

    result = tool.execute("echo hello")

    assert result["success"] is True
    assert result["stdout"] == "fake output"
    assert result["exit_code"] == 0
    assert backend.last_command == "echo hello"
    assert backend.last_timeout == 30
    assert backend.last_cwd == str(tmp_path)


def test_execute_command_custom_options(tmp_path: Path):
    backend = FakeExecutionBackend()
    context = ToolContext(tmp_path)
    tool = ExecuteCommandTool(context, backend=backend)

    result = tool.execute(
        "pytest -q",
        timeout=120,
        cwd="/tmp",
    )

    assert result["success"] is True
    assert backend.last_command == "pytest -q"
    assert backend.last_timeout == 120
    assert backend.last_cwd == "/tmp"


def test_execute_command_empty_command(tmp_path: Path):
    backend = FakeExecutionBackend()
    tool = ExecuteCommandTool(
        ToolContext(tmp_path),
        backend=backend,
    )

    result = tool.execute("   ")

    assert result["success"] is False
    assert result["error"] == "Command must not be empty."
    assert backend.last_command is None


def test_execute_command_invalid_timeout(tmp_path: Path):
    backend = FakeExecutionBackend()
    tool = ExecuteCommandTool(
        ToolContext(tmp_path),
        backend=backend,
    )

    result = tool.execute(
        "echo hello",
        timeout=0,
    )

    assert result["success"] is False
    assert result["error"] == (
        "Timeout must be greater than 0 seconds."
    )
    assert backend.last_command is None


def test_execute_command_timeout_too_large(tmp_path: Path):
    backend = FakeExecutionBackend()
    tool = ExecuteCommandTool(
        ToolContext(tmp_path),
        backend=backend,
    )

    result = tool.execute(
        "echo hello",
        timeout=301,
    )

    assert result["success"] is False
    assert result["error"] == (
        "Timeout cannot exceed 300 seconds."
    )
    assert backend.last_command is None


def test_execute_command_schema(tmp_path: Path):
    tool = ExecuteCommandTool(
        ToolContext(tmp_path),
        backend=FakeExecutionBackend(),
    )

    schema = tool.schema()

    assert schema["type"] == "function"
    assert schema["function"]["name"] == "execute_command"

    parameters = schema["function"]["parameters"]

    assert "command" in parameters["properties"]
    assert "timeout" in parameters["properties"]
    assert "cwd" in parameters["properties"]
    assert parameters["required"] == ["command"]
