import logging
import time

from models.agent_workflow import WorkflowResult
from models.session import Message, MessageRole
from services.agent_workflows.workflow import AgentWorkflowService
from services.agent_workflows.notifier import WorkflowNotifier
from services.agent_workflows.results import WorkflowResultService
from services.agents.agent import (
    WorkflowExecutionAgent,
    WorkflowExecutionPromptVars,
    WorkflowExecutionAgentRuntimeContext,
)
from services.agent_reminder import AgentReminderService
from services.user_context import (
    UserConversationNotesService,
    UserProfileService,
)

logger = logging.getLogger(__name__)


class WorkflowRunner:
    def __init__(
        self,
        workflow_execution_agent: WorkflowExecutionAgent,
        agent_workflow_service: AgentWorkflowService,
        workflow_result_service: WorkflowResultService,
        user_profile_service: UserProfileService,
        user_conversation_notes_service: UserConversationNotesService,
        agent_reminder_service: AgentReminderService,
        notifier: WorkflowNotifier,
    ):
        self._agent = workflow_execution_agent
        self._workflow_service = agent_workflow_service
        self._workflow_result_service = workflow_result_service
        self._user_profile_service = user_profile_service
        self._user_conversation_notes_service = user_conversation_notes_service
        self._agent_reminder_service = agent_reminder_service
        self._notifier = notifier

    async def run_due_workflows(self) -> None:
        failed_workflows = []
        while True:
            workflow = await self._workflow_service.claim_next_due_workflow(exclude_ids=failed_workflows)
            if not workflow:
                break
            try:
                await self._run_workflow(workflow)
                time.sleep(90)
            except Exception as e:
                logger.exception(
                    "Failed to run workflow %s: %s",
                    workflow.workflow_id,
                    str(e),
                )
                await self._workflow_service.release_workflow_lock(workflow.workflow_id)
                failed_workflows.append(workflow.workflow_id)

    async def _run_workflow(self, workflow) -> None:
        client_profile = await self._user_profile_service.get_client_profile()

        # Single-turn synthetic conversation — no history, just the workflow description
        conversation = [Message(role=MessageRole.USER, content=workflow.description)]

        runtime_context = WorkflowExecutionAgentRuntimeContext(
            workflow_result_service=self._workflow_result_service,
            user_conversation_notes_service=self._user_conversation_notes_service,
        )

        agent_response = await self._agent.generate_response(
            conversation=conversation,
            runtime_context=runtime_context,
            system_prompt_placeholder_values=WorkflowExecutionPromptVars(
                client_profile=client_profile,
            ),
        )

        result = WorkflowResult(
            result_id="",  # assigned when the result is stored
            workflow_id=workflow.workflow_id,
            workflow_name=workflow.name,
            output=agent_response.response,
            ran_at="",  # stamped when the result is stored
        )
        # Storing the result also advances next_run_at and releases the lock
        await self._notifier.notify(result)
