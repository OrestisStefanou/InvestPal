import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from config import settings
from repos.db import connect


@dataclass
class UserProfileNoteRow:
    id: str
    note: str
    created_at: datetime
    outdated: bool


class UserProfileNotesTable:
    def __init__(self, db_path: str = settings.TURSO_DB_PATH):
        self._db_path = db_path
        self._table_name = "user_profile_notes"

    def get_user_profile_notes(
        self, include_outdated: bool = False
    ) -> list[UserProfileNoteRow]:
        query = f"SELECT id, note, created_at, outdated FROM {self._table_name}"
        if not include_outdated:
            query += " WHERE outdated = 0"

        with connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        results = []
        for row in rows:
            created_at_dt = datetime.fromisoformat(row[2])
            results.append(
                UserProfileNoteRow(
                    id=row[0],
                    note=row[1],
                    created_at=created_at_dt,
                    outdated=bool(row[3]),
                )
            )
        return results

    def create_user_profile_note(self, note: str) -> UserProfileNoteRow:
        note_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        created_at_str = created_at.isoformat()

        with connect(self._db_path) as conn:
            conn.execute(
                f"INSERT INTO {self._table_name} (id, note, created_at, outdated) VALUES (?, ?, ?, 0)",
                (note_id, note, created_at_str),
            )

        return UserProfileNoteRow(
            id=note_id, note=note, created_at=created_at, outdated=False
        )

    def mark_as_outdated(self, note_id: str) -> bool:
        with connect(self._db_path) as conn:
            cursor = conn.execute(
                f"UPDATE {self._table_name} SET outdated = 1 WHERE id = ?", (note_id,)
            )
            return cursor.rowcount > 0
