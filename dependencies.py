from fastapi import (
    Depends,
    Request,
    HTTPException,
)
from langchain_mcp_adapters.client import MultiServerMCPClient
from pymongo import AsyncMongoClient

from config import settings
from services.agent import InvestmentAdvisorAgentService
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


def get_mcp_client():
    mcp_server_client = MultiServerMCPClient(
        {
            settings.MCP_SERVER_NAME: {
                "transport": "streamable_http",  # HTTP-based remote server
                "url": settings.MCP_SERVER_URL,
            }
        }
    )    
    return mcp_server_client


def get_session_service(
    db_client: AsyncMongoClient = Depends(get_db_client),
) -> SessionService:
    return MongoDBSessionService(mongo_client=db_client)


def get_user_context_service(
    db_client: AsyncMongoClient = Depends(get_db_client),
) -> UserContextService:
    return MongoDBUserContextService(mongo_client=db_client)


def get_chat_service(
    db_client: AsyncMongoClient = Depends(get_db_client),
    mcp_client: MultiServerMCPClient = Depends(get_mcp_client),
) -> ChatService:
    session_service = get_session_service(db_client)
    user_context_service = get_user_context_service(db_client)
    agent_service = InvestmentAdvisorAgentService(mcp_client=mcp_client, user_context_service=user_context_service)
    return AgenticChatService(session_service, agent_service)
