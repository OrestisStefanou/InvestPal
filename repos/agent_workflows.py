import uuid
from dataclasses import dataclass
from datetime import datetime

from config import settings
from repos.db import connect, connection, first_row


@dataclass
class AgentWorkflowRow:
    id: str
    name: str
    description: str
    schedule: str
    status: str
    created_at: str
    last_run_at: str | None
    next_run_at: str | None


_WORKFLOW_COLUMNS = (
    "id, name, description, schedule, status, created_at, last_run_at, next_run_at"
)


def _to_workflow_row(row) -> AgentWorkflowRow:
    return AgentWorkflowRow(
        id=row[0],
        name=row[1],
        description=row[2],
        schedule=row[3],
        status=row[4],
        created_at=row[5],
        last_run_at=row[6],
        next_run_at=row[7],
    )


class AgentWorkflowsTable:
    """Scheduled workflows. Their run results live in `WorkflowResultsTable`."""

    def __init__(self, db_path: str = settings.TURSO_DB_PATH):
        self._db_path = db_path
        self._table_name = "agent_workflows"

    def create_workflow(
        self,
        name: str,
        description: str,
        schedule: str,
        status: str,
        next_run_at: str | None,
    ) -> AgentWorkflowRow:
        workflow_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()

        with connect(self._db_path) as conn:
            conn.execute(
                f"INSERT INTO {self._table_name} "
                "(id, name, description, schedule, status, created_at, last_run_at, next_run_at) "
                "VALUES (?, ?, ?, ?, ?, ?, NULL, ?)",
                (workflow_id, name, description, schedule, status, created_at, next_run_at),
            )

        return AgentWorkflowRow(
            id=workflow_id,
            name=name,
            description=description,
            schedule=schedule,
            status=status,
            created_at=created_at,
            last_run_at=None,
            next_run_at=next_run_at,
        )

    def get_workflows(self) -> list[AgentWorkflowRow]:
        with connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT {_WORKFLOW_COLUMNS} FROM {self._table_name} ORDER BY created_at DESC"
            )
            rows = cursor.fetchall()

        return [_to_workflow_row(row) for row in rows]

    def get_workflow(self, workflow_id: str) -> AgentWorkflowRow | None:
        with connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT {_WORKFLOW_COLUMNS} FROM {self._table_name} WHERE id = ?",
                (workflow_id,),
            )
            row = cursor.fetchone()

        return _to_workflow_row(row) if row else None

    def claim_next_due_workflow(
        self,
        now: str,
        running_status: str,
        active_status: str,
        exclude_ids: list[str] | None = None,
    ) -> AgentWorkflowRow | None:
        """Atomically flip one due workflow to `running_status` and return it."""
        select = (
            f"SELECT id FROM {self._table_name} "
            "WHERE status = ? AND next_run_at IS NOT NULL AND next_run_at <= ?"
        )
        params: list = [active_status, now]

        if exclude_ids:
            placeholders = ", ".join("?" for _ in exclude_ids)
            select += f" AND id NOT IN ({placeholders})"
            params.extend(exclude_ids)

        select += " ORDER BY next_run_at LIMIT 1"

        with connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {self._table_name} SET status = ? WHERE id = ({select}) "
                f"RETURNING {_WORKFLOW_COLUMNS}",
                (running_status, *params),
            )
            row = first_row(cursor)

        return _to_workflow_row(row) if row else None

    def release_lock(self, workflow_id: str, active_status: str, running_status: str) -> None:
        with connect(self._db_path) as conn:
            conn.execute(
                f"UPDATE {self._table_name} SET status = ? WHERE id = ? AND status = ?",
                (active_status, workflow_id, running_status),
            )

    def update_workflow(
        self,
        workflow_id: str,
        name: str | None = None,
        description: str | None = None,
        schedule: str | None = None,
        status: str | None = None,
        next_run_at: str | None = None,
    ) -> AgentWorkflowRow | None:
        assignments = []
        params: list = []
        for column, value in (
            ("name", name),
            ("description", description),
            ("schedule", schedule),
            ("status", status),
            ("next_run_at", next_run_at),
        ):
            if value is not None:
                assignments.append(f"{column} = ?")
                params.append(value)

        if not assignments:
            return self.get_workflow(workflow_id)

        with connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {self._table_name} SET {', '.join(assignments)} WHERE id = ? "
                f"RETURNING {_WORKFLOW_COLUMNS}",
                (*params, workflow_id),
            )
            row = first_row(cursor)

        return _to_workflow_row(row) if row else None

    def delete_workflow(self, workflow_id: str) -> bool:
        with connect(self._db_path) as conn:
            cursor = conn.execute(
                f"DELETE FROM {self._table_name} WHERE id = ?", (workflow_id,)
            )
            return cursor.rowcount > 0

    def advance_schedule(
        self,
        workflow_id: str,
        ran_at: str,
        next_run_at: str,
        active_status: str,
        conn=None,
    ) -> None:
        """Mark a run as finished: record when it ran, when it next runs, and unlock it.

        Accepts a connection because this has to commit together with the result
        that triggered it, otherwise a stored result could leave the workflow
        still due and it would run again on the next tick. See
        `WorkflowResultsTable.store_result`.
        """
        with connection(self._db_path, conn) as c:
            c.execute(
                f"UPDATE {self._table_name} "
                "SET last_run_at = ?, next_run_at = ?, status = ? WHERE id = ?",
                (ran_at, next_run_at, active_status, workflow_id),
            )
