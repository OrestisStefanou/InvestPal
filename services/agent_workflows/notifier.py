from abc import ABC, abstractmethod

from models.agent_workflow import WorkflowResult
from services.agent_workflows.results import WorkflowResultService


class WorkflowNotifier(ABC):
    @abstractmethod
    async def notify(self, result: WorkflowResult) -> None:
        pass


class PersistingWorkflowNotifier(WorkflowNotifier):
    """v1 notifier — persists the result, which also advances the workflow's schedule."""

    def __init__(self, workflow_result_service: WorkflowResultService):
        self._workflow_result_service = workflow_result_service

    async def notify(self, result: WorkflowResult) -> None:
        await self._workflow_result_service.save_result(
            workflow_id=result.workflow_id,
            workflow_name=result.workflow_name,
            output=result.output,
        )
