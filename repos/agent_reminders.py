import uuid
from dataclasses import dataclass
from datetime import datetime

from config import settings
from repos.db import connect


@dataclass
class AgentReminderRow:
    id: str
    description: str
    due_date: str | None
    created_at: str
    deleted_at: str | None


class AgentRemindersTable:
    def __init__(self, db_path: str = settings.TURSO_DB_PATH):
        self._db_path = db_path
        self._table_name = "agent_reminders"

    def create_reminder(
        self, description: str, due_date: str | None = None
    ) -> AgentReminderRow:
        reminder_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()

        with connect(self._db_path) as conn:
            conn.execute(
                f"INSERT INTO {self._table_name} (id, description, due_date, created_at) VALUES (?, ?, ?, ?)",
                (reminder_id, description, due_date, created_at),
            )

        return AgentReminderRow(
            id=reminder_id,
            description=description,
            due_date=due_date,
            created_at=created_at,
            deleted_at=None,
        )

    def get_reminders(self) -> list[AgentReminderRow]:
        query = f"SELECT id, description, due_date, created_at, deleted_at FROM {self._table_name} WHERE deleted_at IS NULL"

        with connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        return [
            AgentReminderRow(
                id=row[0],
                description=row[1],
                due_date=row[2],
                created_at=row[3],
                deleted_at=row[4],
            )
            for row in rows
        ]

    def delete_reminder(self, reminder_id: str) -> bool:
        deleted_at = datetime.now().isoformat()

        with connect(self._db_path) as conn:
            cursor = conn.execute(
                f"UPDATE {self._table_name} SET deleted_at = ? WHERE id = ? AND deleted_at IS NULL",
                (deleted_at, reminder_id),
            )
            return cursor.rowcount > 0

    def update_reminder(
        self,
        reminder_id: str,
        description: str | None = None,
        due_date: str | None = None,
    ) -> AgentReminderRow | None:
        # First check the reminder exists and is not soft-deleted
        with connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT id, description, due_date, created_at, deleted_at FROM {self._table_name} WHERE id = ? AND deleted_at IS NULL",
                (reminder_id,),
            )
            row = cursor.fetchone()

        if not row:
            return None

        current = AgentReminderRow(
            id=row[0],
            description=row[1],
            due_date=row[2],
            created_at=row[3],
            deleted_at=row[4],
        )

        new_description = description if description is not None else current.description
        new_due_date = due_date if due_date is not None else current.due_date

        with connect(self._db_path) as conn:
            conn.execute(
                f"UPDATE {self._table_name} SET description = ?, due_date = ? WHERE id = ? AND deleted_at IS NULL",
                (new_description, new_due_date, reminder_id),
            )

        return AgentReminderRow(
            id=current.id,
            description=new_description,
            due_date=new_due_date,
            created_at=current.created_at,
            deleted_at=None,
        )

    def insert_row(self, row: AgentReminderRow) -> None:
        """Insert a fully-formed row, used for backfill. Skips duplicates."""
        with connect(self._db_path) as conn:
            conn.execute(
                f"INSERT OR IGNORE INTO {self._table_name} (id, description, due_date, created_at, deleted_at) VALUES (?, ?, ?, ?, ?)",
                (row.id, row.description, row.due_date, row.created_at, row.deleted_at),
            )
