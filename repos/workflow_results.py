import uuid
from contextlib import contextmanager
from dataclasses import dataclass

from config import settings
from repos.db import connect, connection


@dataclass
class WorkflowResultRow:
    id: str
    workflow_id: str
    workflow_name: str
    output: str
    ran_at: str


_RESULT_COLUMNS = "id, workflow_id, workflow_name, output, ran_at"


def _to_result_row(row) -> WorkflowResultRow:
    return WorkflowResultRow(
        id=row[0],
        workflow_id=row[1],
        workflow_name=row[2],
        output=row[3],
        ran_at=row[4],
    )


class WorkflowResultsTable:
    """Results of workflow runs.

    Storing a result and advancing the workflow that produced it have to commit
    together, so `store_result` accepts a connection and `transaction` hands
    one out. See `AgentWorkflowsTable.advance_schedule` for the other half.
    """

    def __init__(self, db_path: str = settings.TURSO_DB_PATH):
        self._db_path = db_path
        self._table_name = "workflow_results"

    @contextmanager
    def transaction(self):
        """Open a transaction that several tables in this database can share.

        Pass the yielded connection to each participating repo method. Anything
        that raises inside the block rolls the whole thing back.
        """
        with connect(self._db_path) as conn:
            yield conn

    def store_result(
        self,
        workflow_id: str,
        workflow_name: str,
        output: str,
        ran_at: str,
        conn=None,
    ) -> WorkflowResultRow:
        result_id = str(uuid.uuid4())

        with connection(self._db_path, conn) as c:
            c.execute(
                f"INSERT INTO {self._table_name} ({_RESULT_COLUMNS}) "
                "VALUES (?, ?, ?, ?, ?)",
                (result_id, workflow_id, workflow_name, output, ran_at),
            )

        return WorkflowResultRow(
            id=result_id,
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            output=output,
            ran_at=ran_at,
        )

    def get_results(self, limit: int | None = None) -> list[WorkflowResultRow]:
        query = f"SELECT {_RESULT_COLUMNS} FROM {self._table_name} ORDER BY ran_at DESC"
        params: tuple = ()
        if limit is not None:
            query += " LIMIT ?"
            params = (limit,)

        with connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

        return [_to_result_row(row) for row in rows]
