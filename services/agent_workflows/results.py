import asyncio
import datetime as dt
from abc import ABC, abstractmethod

from models.agent_workflow import WorkflowResult, WorkflowStatus
from repos.agent_workflows import AgentWorkflowsTable, WorkflowResultRow
from services.agent_workflows.workflow import compute_next_run_at


def _row_to_model(row: WorkflowResultRow) -> WorkflowResult:
    return WorkflowResult(
        result_id=row.id,
        workflow_id=row.workflow_id,
        workflow_name=row.workflow_name,
        output=row.output,
        ran_at=row.ran_at,
    )


class WorkflowResultService(ABC):
    @abstractmethod
    async def save_result(
        self,
        workflow_id: str,
        workflow_name: str,
        output: str,
    ) -> WorkflowResult:
        pass

    @abstractmethod
    async def get_results(self, limit: int | None = 10) -> list[WorkflowResult]:
        pass


class TursoWorkflowResultService(WorkflowResultService):
    def __init__(self, table: AgentWorkflowsTable):
        self._table = table

    async def save_result(
        self,
        workflow_id: str,
        workflow_name: str,
        output: str,
    ) -> WorkflowResult:
        """
        Store the result of a run and advance the workflow's schedule.

        Storing a result is what marks a run as finished, so the same operation sets
        last_run_at, computes the next next_run_at from the workflow's cron schedule
        and releases the running lock. Both writes happen in one transaction, so a
        stored result can never leave the workflow due to run again.

        A result for a workflow that no longer exists is still stored, it just has no
        schedule to advance.
        """
        ran_at = dt.datetime.now(dt.timezone.utc).isoformat()

        workflow = await asyncio.to_thread(self._table.get_workflow, workflow_id)
        next_run_at = (
            compute_next_run_at(workflow.schedule, dt.datetime.fromisoformat(ran_at))
            if workflow
            else None
        )

        row = await asyncio.to_thread(
            self._table.record_run,
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            output=output,
            ran_at=ran_at,
            next_run_at=next_run_at,
            active_status=WorkflowStatus.ACTIVE.value,
        )
        return _row_to_model(row)

    async def get_results(self, limit: int | None = 10) -> list[WorkflowResult]:
        rows = await asyncio.to_thread(self._table.get_results, limit)
        return [_row_to_model(row) for row in rows]
