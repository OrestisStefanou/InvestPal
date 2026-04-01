from fastapi import (
    Depends,
    Request,
    HTTPException,
    Header,
)
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
from services.agent_service import InvestmentManagerAgentService
from services.session import (
    MongoDBSessionService, 
    SessionService,
)
from services.chat import (
    ChatService,
    AgenticChatService,
)
from services.user_context import (
    MongoDBUserContextService, 
    UserContextService,
)

def get_db_client(request: Request):
    if not hasattr(request.app.state, "mongodb_client"):
        raise HTTPException(status_code=500, detail="Database not initialized")
    return request.app.state.mongodb_client


def get_mcp_client(
    alpaca_api_key: str | None = Header(None, alias="X-Alpaca-Api-Key"),
    alpaca_api_secret: str | None = Header(None, alias="X-Alpaca-Api-Secret"),
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


def get_chat_service(
    investment_manager_agent_service: InvestmentManagerAgentService = Depends(get_investment_manager_agent_service),
    session_service: SessionService = Depends(get_session_service),
) -> ChatService:
    return AgenticChatService(
        agent_service=investment_manager_agent_service,
        session_service=session_service,
    )
