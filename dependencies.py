from fastapi import (
    Depends,
    Request,
    HTTPException,
)
from langchain.agents.structured_output import ToolStrategy
from langchain_mcp_adapters.client import MultiServerMCPClient
from pymongo import AsyncMongoClient

from config import settings
from services.agents.agent import (
    Agent,
    InvestmentManagerAgent,
    UserContextMemoryManagerAgent,
)
from services.agents.middleware import (
    ToolErrorMiddleware,
    ToolLoggingMiddleware,
)
from services.agent_service import (
    InvestmentAdvisorAgentService,
    InvestmentManagerAgentService,
)
from services.session import (
    MongoDBSessionService, 
    SessionService,
)
from services.chat import (
    ChatService,
    ChatServiceV2,
    AgenticChatService,
    AgenticChatServiceV2,
)
from services.user_context import (
    MongoDBUserContextService, 
    UserContextService,
)

def get_db_client(request: Request):
    if not hasattr(request.app.state, "mongodb_client"):
        raise HTTPException(status_code=500, detail="Database not initialized")
    return request.app.state.mongodb_client


def get_mcp_client():
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
        }
    
    if settings.COINBASE_MCP_SERVER_URL:
        connections[settings.COINBASE_MCP_SERVER_NAME] = {
            "transport": "streamable_http",
            "url": settings.COINBASE_MCP_SERVER_URL,
        }

    mcp_server_client = MultiServerMCPClient(connections)

    return mcp_server_client


def get_session_service(
    db_client: AsyncMongoClient = Depends(get_db_client),
) -> SessionService:
    return MongoDBSessionService(mongo_client=db_client)


def get_user_context_service(
    db_client: AsyncMongoClient = Depends(get_db_client),
) -> UserContextService:
    return MongoDBUserContextService(mongo_client=db_client)


# TODO: Remove this
def get_chat_service(
    db_client: AsyncMongoClient = Depends(get_db_client),
    mcp_client: MultiServerMCPClient = Depends(get_mcp_client),
) -> ChatService:
    session_service = get_session_service(db_client)
    user_context_service = get_user_context_service(db_client)
    agent_service = InvestmentAdvisorAgentService(mcp_client=mcp_client, user_context_service=user_context_service)
    return AgenticChatService(session_service, agent_service)


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


# TODO
def get_investment_manager_agent_service(
    investment_manager_agent: InvestmentManagerAgent = Depends(get_investment_manager_agent),
    user_context_memory_manager_agent: UserContextMemoryManagerAgent = Depends(get_user_context_memory_manager_agent),
    user_context_service: UserContextService = Depends(get_user_context_service),
) -> InvestmentManagerAgentService:
    return InvestmentManagerAgentService(
        investment_manager_agent=investment_manager_agent,
        user_context_memory_manager_agent=user_context_memory_manager_agent,
        user_context_service=user_context_service,
    )


# TODO: This should replace the existing get_chat_service
def get_chat_service_v2(
    investment_manager_agent_service: InvestmentManagerAgentService = Depends(get_investment_manager_agent_service),
    session_service: SessionService = Depends(get_session_service),
) -> ChatServiceV2:
    return AgenticChatServiceV2(
        agent_service=investment_manager_agent_service,
        session_service=session_service,
    )
