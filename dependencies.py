from fastapi import (
    Depends,
    Header,
)
from langchain_mcp_adapters.client import MultiServerMCPClient

from config import settings
from services.agents.agent import (
    Agent,
    InvestmentManagerAgent,
    UserContextMemoryManagerAgent,
)
from services.agents.middleware import (
    ToolErrorMiddleware,
    ToolLoggingMiddleware,
    ToolTokenRateLimitMiddleware,
)
from services.agent_service import InvestmentManagerAgentService
from services.session import (
    SessionService,
    TursoSessionService,
)
from repos.sessions import SessionsTable
from services.chat import (
    ChatService,
    AgenticChatService,
)
from services.user_context import (
    UserConversationNotesService,
    UserProfileService,
)
from repos.user_conversation_notes import UserConversationNotesTable
from repos.user_profile_notes import UserProfileNotesTable
from services.agent_reminder import (
    TursoAgentReminderService,
    AgentReminderService,
)
from repos.agent_reminders import AgentRemindersTable
from services.agent_workflows.workflow import (
    AgentWorkflowService,
    TursoAgentWorkflowService,
)
from services.agent_workflows.results import (
    WorkflowResultService,
    TursoWorkflowResultService,
)
from services.agent_workflows.notifier import (
    WorkflowNotifier,
    PersistingWorkflowNotifier,
)
from repos.agent_workflows import AgentWorkflowsTable
from services.agent_workflows.runner import WorkflowRunner
from services.agents.agent import WorkflowExecutionAgent

def get_mcp_client(
    alpaca_api_key: str | None = Header(None, alias="X-Alpaca-Api-Key"),
    alpaca_api_secret: str | None = Header(None, alias="X-Alpaca-Api-Secret"),
    coinbase_api_key: str | None = Header(None, alias="X-Coinbase-Api-Key"),
    coinbase_api_secret: str | None = Header(None, alias="X-Coinbase-Api-Secret"),  # base64 encoded
):
    connections = {
        settings.MARKET_DATA_MCP_SERVER_NAME: {
            "transport": "streamable_http",
            "url": settings.MARKET_DATA_MCP_SERVER_URL,
        }
    }

    if settings.ALPACA_MCP_SERVER_URL:
        connections[settings.ALPACA_MCP_SERVER_NAME] = {
            "transport": "streamable_http",
            "url": settings.ALPACA_MCP_SERVER_URL,
            "headers": {
                "X-Alpaca-Api-Key": alpaca_api_key or "",
                "X-Alpaca-Api-Secret": alpaca_api_secret or "",
            }
        }
    
    if settings.COINBASE_MCP_SERVER_URL:
        connections[settings.COINBASE_MCP_SERVER_NAME] = {
            "transport": "streamable_http",
            "url": settings.COINBASE_MCP_SERVER_URL,
            "headers": {
                "X-Coinbase-Api-Key": coinbase_api_key or "",
                "X-Coinbase-Api-Secret": coinbase_api_secret or "",
            }
        }

    mcp_server_client = MultiServerMCPClient(connections)

    return mcp_server_client


def get_session_service() -> SessionService:
    return TursoSessionService(table=SessionsTable())


def get_user_profile_service() -> UserProfileService:
    table = UserProfileNotesTable()
    return UserProfileService(table=table)


def get_user_conversation_notes_service() -> UserConversationNotesService:
    table = UserConversationNotesTable()
    return UserConversationNotesService(table=table)


def get_agent_reminder_service() -> AgentReminderService:
    table = AgentRemindersTable()
    return TursoAgentReminderService(table=table)


async def get_investment_manager_agent(
    mcp_client: MultiServerMCPClient = Depends(get_mcp_client),
) -> InvestmentManagerAgent:
    agent = await InvestmentManagerAgent.create(
        mcp_client=mcp_client,
        middleware=[ToolErrorMiddleware(), ToolLoggingMiddleware()],
    )
    return agent


async def get_user_context_memory_manager_agent() -> UserContextMemoryManagerAgent:
    return UserContextMemoryManagerAgent(
        middleware=[ToolErrorMiddleware(), ToolLoggingMiddleware()],
    )


def get_agent_workflows_table() -> AgentWorkflowsTable:
    return AgentWorkflowsTable()


def get_agent_workflow_service(
    table: AgentWorkflowsTable = Depends(get_agent_workflows_table),
) -> AgentWorkflowService:
    return TursoAgentWorkflowService(table=table)


def get_workflow_result_service(
    table: AgentWorkflowsTable = Depends(get_agent_workflows_table),
) -> WorkflowResultService:
    return TursoWorkflowResultService(table=table)


def get_workflow_notifier(
    workflow_result_service: WorkflowResultService = Depends(get_workflow_result_service),
) -> WorkflowNotifier:
    return PersistingWorkflowNotifier(workflow_result_service=workflow_result_service)


async def get_workflow_runner(
    mcp_client: MultiServerMCPClient = Depends(get_mcp_client),
    agent_workflow_service: AgentWorkflowService = Depends(get_agent_workflow_service),
    workflow_result_service: WorkflowResultService = Depends(get_workflow_result_service),
    user_profile_service: UserProfileService = Depends(get_user_profile_service),
    user_conversation_notes_service: UserConversationNotesService = Depends(get_user_conversation_notes_service),
    agent_reminder_service: AgentReminderService = Depends(get_agent_reminder_service),
    notifier: WorkflowNotifier = Depends(get_workflow_notifier),
) -> WorkflowRunner:
    agent = await WorkflowExecutionAgent.create(
        mcp_client=mcp_client,
        middleware=[
            ToolErrorMiddleware(),
            ToolLoggingMiddleware(),
            ToolTokenRateLimitMiddleware(),
        ],
    )
    return WorkflowRunner(
        workflow_execution_agent=agent,
        agent_workflow_service=agent_workflow_service,
        workflow_result_service=workflow_result_service,
        user_profile_service=user_profile_service,
        user_conversation_notes_service=user_conversation_notes_service,
        agent_reminder_service=agent_reminder_service,
        notifier=notifier,
    )


def get_investment_manager_agent_service(
    investment_manager_agent: InvestmentManagerAgent = Depends(get_investment_manager_agent),
    user_context_memory_manager_agent: UserContextMemoryManagerAgent = Depends(get_user_context_memory_manager_agent),
    user_profile_service: UserProfileService = Depends(get_user_profile_service),
    user_conversation_notes_service: UserConversationNotesService = Depends(get_user_conversation_notes_service),
    agent_reminder_service: AgentReminderService = Depends(get_agent_reminder_service),
    agent_workflow_service: AgentWorkflowService = Depends(get_agent_workflow_service),
    workflow_result_service: WorkflowResultService = Depends(get_workflow_result_service),
) -> InvestmentManagerAgentService:
    return InvestmentManagerAgentService(
        investment_manager_agent=investment_manager_agent,
        user_context_memory_manager_agent=user_context_memory_manager_agent,
        user_profile_service=user_profile_service,
        user_conversation_notes_service=user_conversation_notes_service,
        agent_reminder_service=agent_reminder_service,
        agent_workflow_service=agent_workflow_service,
        workflow_result_service=workflow_result_service,
    )


def get_chat_service(
    investment_manager_agent_service: InvestmentManagerAgentService = Depends(get_investment_manager_agent_service),
    session_service: SessionService = Depends(get_session_service),
) -> ChatService:
    return AgenticChatService(
        agent_service=investment_manager_agent_service,
        session_service=session_service,
    )
