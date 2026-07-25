from dataclasses import dataclass
from datetime import datetime, timezone

from config import settings
from repos.db import connect


@dataclass
class SessionRow:
    id: str
    name: str
    created_at: str


@dataclass
class SessionMessageRow:
    role: str
    content: str
    created_at: str | None


class SessionsTable:
    """Sessions and the messages exchanged in them."""

    def __init__(self, db_path: str = settings.TURSO_DB_PATH):
        self._db_path = db_path
        self._table_name = "sessions"
        self._messages_table_name = "session_messages"

    def create_session(self, session_id: str, name: str) -> SessionRow:
        created_at = datetime.now(timezone.utc).isoformat()

        with connect(self._db_path) as conn:
            conn.execute(
                f"INSERT INTO {self._table_name} (id, name, created_at) VALUES (?, ?, ?)",
                (session_id, name, created_at),
            )

        return SessionRow(id=session_id, name=name, created_at=created_at)

    def get_session(self, session_id: str) -> SessionRow | None:
        with connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT id, name, created_at FROM {self._table_name} WHERE id = ?",
                (session_id,),
            )
            row = cursor.fetchone()

        return SessionRow(id=row[0], name=row[1], created_at=row[2]) if row else None

    def get_sessions(self) -> list[SessionRow]:
        with connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT id, name, created_at FROM {self._table_name} ORDER BY created_at DESC"
            )
            rows = cursor.fetchall()

        return [SessionRow(id=row[0], name=row[1], created_at=row[2]) for row in rows]

    def get_messages(self, session_id: str) -> list[SessionMessageRow]:
        """Messages in the order they were added."""
        with connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT role, content, created_at FROM {self._messages_table_name} "
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
                f"INSERT INTO {self._messages_table_name} "
                "(session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (session_id, role, content, created_at),
            )
