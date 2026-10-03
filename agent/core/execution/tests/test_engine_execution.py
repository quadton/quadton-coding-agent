from pathlib import Path

from agent.core.engine import AgentEngine
from agent.core.execution.base import ExecutionBackend, ExecutionResult
from agent.core.tools.registry import ToolRegistry


class FakeExecutionBackend(ExecutionBackend):
    """Fake execution backend for engine integration tests."""

    name = "fake"

    def execute(
        self,
        command: str,
        *,
        timeout: int = 30,
        cwd: str | None = None,
    ) -> ExecutionResult:
        return ExecutionResult(
            success=True,
            stdout="fake output",
            stderr="",
            exit_code=0,
        )

    def is_available(self) -> bool:
        return True


class FakeProvider:
    """Minimal provider stub for engine construction."""

    name = "openrouter"

    def send(self, *args, **kwargs):
        raise AssertionError(
            "Provider should not be called in this test."
        )


def test_engine_uses_injected_execution_backend(tmp_path: Path):
    backend = FakeExecutionBackend()

    engine = AgentEngine(
        provider=FakeProvider(),
        model="test-model",
        project_root=tmp_path,
        execution_backend=backend,
    )

    execute_tool = engine.tools.get("execute_command")

    assert execute_tool is not None
    assert execute_tool.backend is backend


def test_engine_exposes_execution_backend(tmp_path: Path):
    backend = FakeExecutionBackend()

    engine = AgentEngine(
        provider=FakeProvider(),
        model="test-model",
        project_root=tmp_path,
        execution_backend=backend,
    )

    assert engine.execution_backend is backend


def test_engine_preserves_custom_tool_registry(tmp_path: Path):
    backend = FakeExecutionBackend()
    custom_registry = ToolRegistry()

    engine = AgentEngine(
        provider=FakeProvider(),
        model="test-model",
        project_root=tmp_path,
        execution_backend=backend,
        tools=custom_registry,
    )

    assert engine.tools is custom_registry
