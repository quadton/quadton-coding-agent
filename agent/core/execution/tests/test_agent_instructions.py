from pathlib import Path

from agent.core.engine import AgentEngine
from agent.core.execution.local import LocalExecutionBackend


class FakeProvider:
    """Minimal provider for testing agent instructions."""

    name = "openrouter"

    def send(self, messages, *, model, tools):
        return {
            "message": {
                "role": "assistant",
                "content": "Done.",
            }
        }


def create_engine(
    project_root: Path,
    system_prompt: str | None = None,
):
    return AgentEngine(
        provider=FakeProvider(),
        model="test-model",
        project_root=project_root,
        execution_backend=LocalExecutionBackend(),
        system_prompt=system_prompt,
    )


def test_engine_loads_agent_md(
    tmp_path: Path,
):
    agent_file = tmp_path / "AGENT.md"

    agent_file.write_text(
        "# Test Instructions\n\n"
        "Always run pytest after changes.",
        encoding="utf-8",
    )

    engine = create_engine(tmp_path)

    assert engine.system_prompt == (
        "# Test Instructions\n\n"
        "Always run pytest after changes."
    )

    history = engine.get_history()

    assert history[0]["role"] == "system"
    assert history[0]["content"] == engine.system_prompt


def test_engine_handles_missing_agent_md(
    tmp_path: Path,
):
    engine = create_engine(tmp_path)

    assert engine.system_prompt is None

    assert engine.get_history() == []


def test_explicit_system_prompt_overrides_agent_md(
    tmp_path: Path,
):
    agent_file = tmp_path / "AGENT.md"

    agent_file.write_text(
        "Project instructions.",
        encoding="utf-8",
    )

    engine = create_engine(
        tmp_path,
        system_prompt="Explicit instructions.",
    )

    assert engine.system_prompt == (
        "Explicit instructions."
    )

    assert engine.get_history()[0]["content"] == (
        "Explicit instructions."
    )


def test_clear_history_preserves_agent_instructions(
    tmp_path: Path,
):
    agent_file = tmp_path / "AGENT.md"

    agent_file.write_text(
        "Persistent project instructions.",
        encoding="utf-8",
    )

    engine = create_engine(tmp_path)

    engine.send_message("Hello")
    engine.clear_history()

    history = engine.get_history()

    assert len(history) == 1
    assert history[0]["role"] == "system"
    assert history[0]["content"] == (
        "Persistent project instructions."
    )
