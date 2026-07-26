import uuid
from dataclasses import dataclass
from datetime import datetime

from config import settings
from repos.db import connect


@dataclass
class UserConversationNoteRow:
    id: str
    date: str
    note: str
    created_at: str


class UserConversationNotesTable:
    def __init__(self, db_path: str = settings.TURSO_DB_PATH):
        self._db_path = db_path
        self._table_name = "user_conversation_notes"

    def create_note(self, date: str, note: str) -> UserConversationNoteRow:
        note_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()

        with connect(self._db_path) as conn:
            conn.execute(
                f"INSERT INTO {self._table_name} (id, date, note, created_at) VALUES (?, ?, ?, ?)",
                (note_id, date, note, created_at),
            )

        return UserConversationNoteRow(
            id=note_id, date=date, note=note, created_at=created_at
        )

    def get_notes(self, limit: int | None = None) -> list[UserConversationNoteRow]:
        query = (
            f"SELECT id, date, note, created_at FROM {self._table_name} "
            "ORDER BY date DESC, created_at DESC"
        )
        params: tuple = ()
        if limit is not None:
            query += " LIMIT ?"
            params = (limit,)

        with connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

        return [
            UserConversationNoteRow(
                id=row[0], date=row[1], note=row[2], created_at=row[3]
            )
            for row in rows
        ]
