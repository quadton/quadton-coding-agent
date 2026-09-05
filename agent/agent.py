from pathlib import Path
from typing import Any

from agent.core.engine import AgentEngine


class QuadtonAgent:
    """High-level autonomous coding agent."""

    def __init__(
        self,
        engine: AgentEngine | None = None,
        instructions_path: str | Path = "AGENT.md",
    ) -> None:
        self.instructions_path = Path(
            instructions_path
        ).resolve()

        self.instructions = self._load_instructions()

        self.engine = engine or AgentEngine(
            system_prompt=self.instructions,
        )

    def _load_instructions(self) -> str:
        """Load the project's AGENT.md instructions."""

        if not self.instructions_path.exists():
            raise FileNotFoundError(
                f"Agent instructions not found: "
                f"{self.instructions_path}"
            )

        if not self.instructions_path.is_file():
            raise ValueError(
                f"Agent instructions path is not a file: "
                f"{self.instructions_path}"
            )

        try:
            return self.instructions_path.read_text(
                encoding="utf-8"
            )

        except OSError as exc:
            raise RuntimeError(
                f"Failed to read agent instructions: "
                f"{exc}"
            ) from exc

    def run(
        self,
        task: str,
    ) -> dict[str, Any]:
        """Run the agent against a user task."""

        if not task.strip():
            raise ValueError(
                "Agent task cannot be empty."
            )

        return self.engine.send_message(
            task
        )

    def get_history(
        self,
    ) -> list[dict[str, Any]]:
        """Return the current agent conversation history."""

        return self.engine.get_history()

    def clear_history(self) -> None:
        """Clear the conversation while preserving AGENT.md."""

        self.engine.clear_history()
