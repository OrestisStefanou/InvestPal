import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime

import turso

from config import settings


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


@dataclass
class WorkflowResultRow:
    id: str
    workflow_id: str
    workflow_name: str
    output: str
    ran_at: str


_WORKFLOW_COLUMNS = (
    "id, name, description, schedule, status, created_at, last_run_at, next_run_at"
)
_RESULT_COLUMNS = "id, workflow_id, workflow_name, output, ran_at"


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


def _to_result_row(row) -> WorkflowResultRow:
    return WorkflowResultRow(
        id=row[0],
        workflow_id=row[1],
        workflow_name=row[2],
        output=row[3],
        ran_at=row[4],
    )


class AgentWorkflowsTable:
    """Workflows and the results of their runs.

    Both tables live behind one class because recording a run touches both in a
    single transaction.
    """

    def __init__(self, db_path: str = settings.TURSO_DB_PATH):
        self._db_path = db_path
        self._table_name = "agent_workflows"
        self._results_table_name = "workflow_results"

    @contextmanager
    def _connect(self):
        """Commit on success, roll back on error, and always close.

        turso's own `with connection` commits but does not close, which leaks the
        connection and the lock it holds.
        """
        conn = turso.connect(self._db_path)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def _first(cursor):
        """Read one row from a RETURNING statement.

        Must be fetchall, not fetchone: turso leaves an UPDATE ... RETURNING
        statement un-finalized after fetchone, and the next commit on that
        connection then fails with "database is locked".
        """
        rows = cursor.fetchall()
        return rows[0] if rows else None

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

        with self._connect() as conn:
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
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT {_WORKFLOW_COLUMNS} FROM {self._table_name} ORDER BY created_at DESC"
            )
            rows = cursor.fetchall()

        return [_to_workflow_row(row) for row in rows]

    def get_workflow(self, workflow_id: str) -> AgentWorkflowRow | None:
        with self._connect() as conn:
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

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {self._table_name} SET status = ? WHERE id = ({select}) "
                f"RETURNING {_WORKFLOW_COLUMNS}",
                (running_status, *params),
            )
            row = self._first(cursor)

        return _to_workflow_row(row) if row else None

    def release_lock(self, workflow_id: str, active_status: str, running_status: str) -> None:
        with self._connect() as conn:
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

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {self._table_name} SET {', '.join(assignments)} WHERE id = ? "
                f"RETURNING {_WORKFLOW_COLUMNS}",
                (*params, workflow_id),
            )
            row = self._first(cursor)

        return _to_workflow_row(row) if row else None

    def delete_workflow(self, workflow_id: str) -> bool:
        with self._connect() as conn:
            cursor = conn.execute(
                f"DELETE FROM {self._table_name} WHERE id = ?", (workflow_id,)
            )
            return cursor.rowcount > 0

    def record_run(
        self,
        workflow_id: str,
        workflow_name: str,
        output: str,
        ran_at: str,
        next_run_at: str | None,
        active_status: str,
    ) -> WorkflowResultRow:
        """Store a run's result and advance the workflow's schedule, in one transaction.

        The workflow update is skipped when `next_run_at` is None, which is the case
        when the workflow no longer exists. The result is still stored, since results
        outlive the workflow that produced them.
        """
        result_id = str(uuid.uuid4())

        with self._connect() as conn:
            conn.execute(
                f"INSERT INTO {self._results_table_name} ({_RESULT_COLUMNS}) "
                "VALUES (?, ?, ?, ?, ?)",
                (result_id, workflow_id, workflow_name, output, ran_at),
            )
            if next_run_at is not None:
                conn.execute(
                    f"UPDATE {self._table_name} "
                    "SET last_run_at = ?, next_run_at = ?, status = ? WHERE id = ?",
                    (ran_at, next_run_at, active_status, workflow_id),
                )

        return WorkflowResultRow(
            id=result_id,
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            output=output,
            ran_at=ran_at,
        )

    def get_results(self, limit: int | None = None) -> list[WorkflowResultRow]:
        query = (
            f"SELECT {_RESULT_COLUMNS} FROM {self._results_table_name} ORDER BY ran_at DESC"
        )
        params: tuple = ()
        if limit is not None:
            query += " LIMIT ?"
            params = (limit,)

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

        return [_to_result_row(row) for row in rows]
