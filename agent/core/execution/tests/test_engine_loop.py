from pathlib import Path

import pytest

from agent.core.engine import AgentEngine
from agent.core.execution.local import LocalExecutionBackend


class FakeProvider:
    """Provider that returns predetermined responses."""

    name = "openrouter"

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def send(self, messages, *, model, tools):
        self.calls += 1

        if not self.responses:
            raise AssertionError(
                "FakeProvider has no remaining responses."
            )

        return self.responses.pop(0)


def test_engine_rejects_invalid_max_iterations(
    tmp_path: Path,
):
    with pytest.raises(
        ValueError,
        match="max_iterations must be greater than 0",
    ):
        AgentEngine(
            provider=FakeProvider([]),
            model="test-model",
            project_root=tmp_path,
            execution_backend=LocalExecutionBackend(),
            max_iterations=0,
        )


def test_engine_stops_after_final_response(
    tmp_path: Path,
):
    provider = FakeProvider(
        [
            {
                "message": {
                    "role": "assistant",
                    "content": "Done.",
                }
            }
        ]
    )

    engine = AgentEngine(
        provider=provider,
        model="test-model",
        project_root=tmp_path,
        execution_backend=LocalExecutionBackend(),
    )

    response = engine.send_message(
        "Finish the task."
    )

    assert response["message"]["content"] == "Done."
    assert provider.calls == 1


def test_engine_executes_tool_then_continues(
    tmp_path: Path,
):
    provider = FakeProvider(
        [
            {
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call-1",
                            "type": "function",
                            "function": {
                                "name": "execute_command",
                                "arguments": (
                                    '{"command":"printf \\"hello\\""}'
                                ),
                            },
                        }
                    ],
                }
            },
            {
                "message": {
                    "role": "assistant",
                    "content": "The command succeeded.",
                }
            },
        ]
    )

    engine = AgentEngine(
        provider=provider,
        model="test-model",
        project_root=tmp_path,
        execution_backend=LocalExecutionBackend(),
    )

    response = engine.send_message(
        "Run the command."
    )

    assert response["message"]["content"] == (
        "The command succeeded."
    )
    assert provider.calls == 2

    history = engine.get_history()

    tool_messages = [
        message
        for message in history
        if message["role"] == "tool"
    ]

    assert len(tool_messages) == 1
    assert "hello" in tool_messages[0]["content"]


def test_engine_stops_at_iteration_limit(
    tmp_path: Path,
):
    tool_response = {
        "message": {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call-1",
                    "type": "function",
                    "function": {
                        "name": "execute_command",
                        "arguments": (
                            '{"command":"printf \\"loop\\""}'
                        ),
                    },
                }
            ],
        }
    }

    provider = FakeProvider(
        [
            tool_response,
            tool_response,
            tool_response,
        ]
    )

    engine = AgentEngine(
        provider=provider,
        model="test-model",
        project_root=tmp_path,
        execution_backend=LocalExecutionBackend(),
        max_iterations=2,
    )

    response = engine.send_message(
        "Keep working."
    )

    assert provider.calls == 2
    assert response["finish_reason"] == "max_iterations"

    content = response["message"]["content"]

    assert "maximum execution limit" in content
    assert "2 tool rounds" in content
