from agent.core.memory import Memory


class Session:
    """Represents the active conversation session."""

    def __init__(
        self,
        memory: Memory,
        session_id: int | None = None,
    ):
        self.memory = memory

        if session_id is None:
            self.session_id = memory.create_session()
        else:
            self.session_id = session_id

    def save_message(
        self,
        role: str,
        content: str,
    ) -> None:
        """Save a message to the active session."""

        self.memory.save_message(
            self.session_id,
            role,
            content,
        )

    def get_messages(self) -> list[dict]:
        """Load all messages from the active session."""

        return self.memory.get_messages(
            self.session_id
        )
