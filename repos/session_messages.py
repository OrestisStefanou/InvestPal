from dataclasses import dataclass

from config import settings
from repos.db import connect


@dataclass
class SessionMessageRow:
    role: str
    content: str
    created_at: str | None


class SessionMessagesTable:
    """Messages exchanged within a session."""

    def __init__(self, db_path: str = settings.TURSO_DB_PATH):
        self._db_path = db_path
        self._table_name = "session_messages"

    def get_messages(self, session_id: str) -> list[SessionMessageRow]:
        """Messages in the order they were added."""
        with connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT role, content, created_at FROM {self._table_name} "
                "WHERE session_id = ? ORDER BY id",
                (session_id,),
            )
            rows = cursor.fetchall()

        return [
            SessionMessageRow(role=row[0], content=row[1], created_at=row[2])
            for row in rows
        ]

    def add_message(
        self, session_id: str, role: str, content: str, created_at: str | None
    ) -> None:
        with connect(self._db_path) as conn:
            conn.execute(
                f"INSERT INTO {self._table_name} "
                "(session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (session_id, role, content, created_at),
            )
