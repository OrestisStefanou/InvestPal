from abc import ABC, abstractmethod

from models.agent_workflow import WorkflowResult
from services.agent_workflows.results import WorkflowResultService


class WorkflowNotifier(ABC):
    @abstractmethod
    async def notify(self, result: WorkflowResult) -> None:
        pass


class MongoDBWorkflowNotifier(WorkflowNotifier):
    """v1 notifier — persists results to MongoDB only."""

    def __init__(self, workflow_result_service: WorkflowResultService):
        self._workflow_result_service = workflow_result_service

    async def notify(self, result: WorkflowResult) -> None:
        await self._workflow_result_service.save_result(
            workflow_id=result.workflow_id,
            user_id=result.user_id,
            workflow_name=result.workflow_name,
            output=result.output,
        )
