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
    EtfExpertAgent,
    CryptoExpertAgent,
    StockAnalystExpertAgent,
    MarketAnalystExpertAgent,
    PortfolioManagerAgent,
)
from services.agents.middleware import (
    ToolErrorMiddleware,
    ToolLoggingMiddleware,
)
from services.agents.tools import (
    ExpertResponse,
)
from services.agent_service import InvestmentAdvisorAgentService
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


def get_chat_service(
    db_client: AsyncMongoClient = Depends(get_db_client),
    mcp_client: MultiServerMCPClient = Depends(get_mcp_client),
) -> ChatService:
    session_service = get_session_service(db_client)
    user_context_service = get_user_context_service(db_client)
    agent_service = InvestmentAdvisorAgentService(mcp_client=mcp_client, user_context_service=user_context_service)
    return AgenticChatService(session_service, agent_service)


async def get_etf_expert_agent(
    mcp_client: MultiServerMCPClient = Depends(get_mcp_client),
) -> EtfExpertAgent:
    market_data_tools = await mcp_client.get_tools(server_name=settings.MARKET_DATA_MCP_SERVER_NAME)
    
    return EtfExpertAgent(
        market_data_tools=market_data_tools,
        middleware=[ToolErrorMiddleware(), ToolLoggingMiddleware()],
    )


async def get_crypto_expert_agent(
    mcp_client: MultiServerMCPClient = Depends(get_mcp_client),
) -> CryptoExpertAgent:
    market_data_tools = await mcp_client.get_tools(server_name=settings.MARKET_DATA_MCP_SERVER_NAME)

    return CryptoExpertAgent(
        market_data_tools=market_data_tools,
        middleware=[ToolErrorMiddleware(), ToolLoggingMiddleware()],
    )


async def get_stock_analyst_expert_agent(
    mcp_client: MultiServerMCPClient = Depends(get_mcp_client),
) -> StockAnalystExpertAgent:
    market_data_tools = await mcp_client.get_tools(server_name=settings.MARKET_DATA_MCP_SERVER_NAME)
    
    return StockAnalystExpertAgent(
        market_data_tools=market_data_tools,
        middleware=[ToolErrorMiddleware(), ToolLoggingMiddleware()],
    )


async def get_market_analyst_expert_agent(
    mcp_client: MultiServerMCPClient = Depends(get_mcp_client),
) -> MarketAnalystExpertAgent:
    market_data_tools = await mcp_client.get_tools(server_name=settings.MARKET_DATA_MCP_SERVER_NAME)
    
    return MarketAnalystExpertAgent(
        market_data_tools=market_data_tools,
        middleware=[ToolErrorMiddleware(), ToolLoggingMiddleware()],
    )


async def get_portfolio_manager_agent(
    mcp_client: MultiServerMCPClient = Depends(get_mcp_client),
) -> PortfolioManagerAgent:
    agent_tools = []
    if settings.ALPACA_MCP_SERVER_URL:
        alpaca_tools = await mcp_client.get_tools(server_name=settings.ALPACA_MCP_SERVER_NAME)
        agent_tools.extend(alpaca_tools)
    
    if settings.COINBASE_MCP_SERVER_URL:
        coinbase_tools = await mcp_client.get_tools(server_name=settings.COINBASE_MCP_SERVER_NAME)
        agent_tools.extend(coinbase_tools)
    
    return PortfolioManagerAgent(
        agent_tools=agent_tools,
        middleware=[ToolErrorMiddleware(), ToolLoggingMiddleware()],
    )
