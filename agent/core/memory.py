import sqlite3
from pathlib import Path
from typing import Any


class Memory:
    """SQLite-backed persistent conversation memory."""

    def __init__(self, db_path: str = "data/agent.db"):
        self.db_path = Path(db_path)

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        """Create a database connection."""

        connection = sqlite3.connect(self.db_path)

        connection.row_factory = sqlite3.Row

        return connection

    def _initialize(self) -> None:
        """Create database tables if they do not exist."""

        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id)
                        REFERENCES sessions(id)
                        ON DELETE CASCADE
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_messages_session
                ON messages(session_id)
                """
            )

            connection.commit()

    def create_session(self, name: str = "New Session") -> int:
        """Create a new conversation session."""

        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO sessions (name)
                VALUES (?)
                """,
                (name,),
            )

            connection.commit()

            return int(cursor.lastrowid)

    def save_message(
        self,
        session_id: int,
        role: str,
        content: str,
    ) -> None:
        """Save a message to a session."""

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO messages (
                    session_id,
                    role,
                    content
                )
                VALUES (?, ?, ?)
                """,
                (
                    session_id,
                    role,
                    content,
                ),
            )

            connection.execute(
                """
                UPDATE sessions
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (session_id,),
            )

            connection.commit()

    def get_messages(
        self,
        session_id: int,
    ) -> list[dict[str, Any]]:
        """Return all messages for a session."""

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT role, content
                FROM messages
                WHERE session_id = ?
                ORDER BY id ASC
                """,
                (session_id,),
            ).fetchall()

        return [
            {
                "role": row["role"],
                "content": row["content"],
            }
            for row in rows
        ]

    def list_sessions(self) -> list[dict[str, Any]]:
        """Return all saved sessions."""

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    name,
                    created_at,
                    updated_at
                FROM sessions
                ORDER BY updated_at DESC
                """
            ).fetchall()

        return [dict(row) for row in rows]

    def delete_session(self, session_id: int) -> None:
        """Delete a session and its messages."""

        with self._connect() as connection:
            connection.execute(
                """
                DELETE FROM sessions
                WHERE id = ?
                """,
                (session_id,),
            )

            connection.commit()
