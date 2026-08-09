import asyncio
import datetime as dt
from abc import ABC, abstractmethod

from croniter import croniter

from models.agent_workflow import AgentWorkflow, WorkflowStatus
from repos.agent_workflows import AgentWorkflowRow, AgentWorkflowsTable


class AgentWorkflowNotFoundError(Exception):
    pass


def compute_next_run_at(schedule: str, base: dt.datetime) -> str:
    """Return the next fire time of a cron expression after `base`, in ISO format."""
    return croniter(schedule, base).get_next(dt.datetime).isoformat()


def row_to_model(row: AgentWorkflowRow) -> AgentWorkflow:
    return AgentWorkflow(
        workflow_id=row.id,
        name=row.name,
        description=row.description,
        schedule=row.schedule,
        status=WorkflowStatus(row.status),
        created_at=row.created_at,
        last_run_at=row.last_run_at,
        next_run_at=row.next_run_at,
    )


class AgentWorkflowService(ABC):
    @abstractmethod
    async def create_workflow(
        self,
        name: str,
        description: str,
        schedule: str,
    ) -> AgentWorkflow:
        pass

    @abstractmethod
    async def get_workflows(self) -> list[AgentWorkflow]:
        pass

    @abstractmethod
    async def claim_next_due_workflow(self, exclude_ids: list[str] | None = None) -> AgentWorkflow | None:
        """Atomically find one due workflow, mark it as 'running', and return it."""
        pass

    @abstractmethod
    async def release_workflow_lock(self, workflow_id: str) -> None:
        """Release the running lock by setting status back to 'active'."""
        pass

    @abstractmethod
    async def update_workflow(
        self,
        workflow_id: str,
        name: str | None = None,
        description: str | None = None,
        schedule: str | None = None,
        status: str | None = None,
    ) -> AgentWorkflow:
        pass

    @abstractmethod
    async def delete_workflow(self, workflow_id: str) -> None:
        pass


class TursoAgentWorkflowService(AgentWorkflowService):
    def __init__(self, table: AgentWorkflowsTable):
        self._table = table

    async def create_workflow(
        self,
        name: str,
        description: str,
        schedule: str,
    ) -> AgentWorkflow:
        now = dt.datetime.now(dt.timezone.utc)
        row = await asyncio.to_thread(
            self._table.create_workflow,
            name=name,
            description=description,
            schedule=schedule,
            status=WorkflowStatus.ACTIVE.value,
            next_run_at=compute_next_run_at(schedule, now),
        )
        return row_to_model(row)

    async def get_workflows(self) -> list[AgentWorkflow]:
        rows = await asyncio.to_thread(self._table.get_workflows)
        return [row_to_model(row) for row in rows]

    async def claim_next_due_workflow(self, exclude_ids: list[str] | None = None) -> AgentWorkflow | None:
        row = await asyncio.to_thread(
            self._table.claim_next_due_workflow,
            now=dt.datetime.now(dt.timezone.utc).isoformat(),
            running_status=WorkflowStatus.RUNNING.value,
            active_status=WorkflowStatus.ACTIVE.value,
            exclude_ids=exclude_ids,
        )
        return row_to_model(row) if row else None

    async def release_workflow_lock(self, workflow_id: str) -> None:
        await asyncio.to_thread(
            self._table.release_lock,
            workflow_id=workflow_id,
            active_status=WorkflowStatus.ACTIVE.value,
            running_status=WorkflowStatus.RUNNING.value,
        )

    async def update_workflow(
        self,
        workflow_id: str,
        name: str | None = None,
        description: str | None = None,
        schedule: str | None = None,
        status: str | None = None,
    ) -> AgentWorkflow:
        # A new schedule re-bases the next run from now
        next_run_at = None
        if schedule is not None:
            next_run_at = compute_next_run_at(schedule, dt.datetime.now(dt.timezone.utc))

        row = await asyncio.to_thread(
            self._table.update_workflow,
            workflow_id=workflow_id,
            name=name,
            description=description,
            schedule=schedule,
            status=WorkflowStatus(status).value if status is not None else None,
            next_run_at=next_run_at,
        )
        if not row:
            raise AgentWorkflowNotFoundError(f"Workflow not found: {workflow_id}")

        return row_to_model(row)

    async def delete_workflow(self, workflow_id: str) -> None:
        deleted = await asyncio.to_thread(self._table.delete_workflow, workflow_id)
        if not deleted:
            raise AgentWorkflowNotFoundError(f"Workflow not found: {workflow_id}")
