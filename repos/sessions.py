from dataclasses import dataclass
from datetime import datetime, timezone

from config import settings
from repos.db import connect


@dataclass
class SessionRow:
    id: str
    name: str
    created_at: str


class SessionsTable:
    """Chat sessions. Their messages live in `SessionMessagesTable`."""

    def __init__(self, db_path: str = settings.TURSO_DB_PATH):
        self._db_path = db_path
        self._table_name = "sessions"

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
