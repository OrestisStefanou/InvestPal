from dataclasses import dataclass

from pydantic import (
    BaseModel,
    Field,
)
from langchain.tools import (
    tool,
    ToolRuntime,
)
from langchain_mcp_adapters.client import MultiServerMCPClient

from models.user_context import (
    UserContext,
    UserPortfolioHolding
)
from models.session import (
    Message,
    MessageRole,
)
from services.user_context import UserContextService
from services.agents.agent import (
    Agent,
    CryptoExpertAgent,
    EtfExpertAgent,
    StockAnalystExpertAgent,
    MarketAnalystExpertAgent,
    PortfolioManagerAgent,
    ExpertResponse,
)


# TODO: Create separate runtime context for each agent service
@dataclass
class ToolRuntimeContext:
    user_context_service: UserContextService
    etf_expert_agent: EtfExpertAgent
    crypto_expert_agent: CryptoExpertAgent
    stock_analyst_expert_agent: StockAnalystExpertAgent
    market_analyst_expert_agent: MarketAnalystExpertAgent
    #mcp_client: MultiServerMCPClient | None = None  # TODO: Remove this since we will add the agents here


class UpdateUserContextToolInput(BaseModel):
    user_id: str = Field(description="The id of the user to update the context for")
    user_profile: dict = Field(description="General information about the user. Must provide the complete user profile as it will replace the existing one.")
    user_portfolio: list[UserPortfolioHolding] = Field(description="List of portfolio holdings. Must provide the complete portfolio as it will replace the existing one.")


@tool(
    "updateUserContext",
    args_schema=UpdateUserContextToolInput,
    description="Update the user context(for the given user_id) including user profile and portfolio holdings. Note: The provided context will completely replace the existing one, so the entire updated object must be provided.",
)
async def update_user_context(
    runtime: ToolRuntime[ToolRuntimeContext],
    user_id: str,
    user_profile: dict,
    user_portfolio: list[UserPortfolioHolding]
) -> UserContext:
    user_context_service = runtime.context.user_context_service
    updated_user_context = await user_context_service.update_user_context(
        user_id=user_id,
        user_profile=user_profile,
        user_portfolio=user_portfolio,
    )

    return updated_user_context


@tool("getUserContext")
async def get_user_context(runtime: ToolRuntime[ToolRuntimeContext], user_id: str) -> UserContext:
    """Get the user context including user profile and portfolio holdings.

    Args:
        user_id: The id of the user to get the context for
    """
    user_context_service = runtime.context.user_context_service
    user_context = await user_context_service.get_user_context(user_id)
    return user_context


@tool("etfExpert")
async def etf_expert(runtime: ToolRuntime[ToolRuntimeContext], question: str) -> str:
    """
    This tool provides access to an ETF expert agent. This is your go to expert in case you want
    information or deep analysis of ETFs (Exchange Traded Funds) or any other ETF related questions. 
    This expert has real time data access to the following:
    - Searching for ETFs based on various criteria
    - Detailed information and overview of specific ETFs

    IMPORTANT: The etf expert is stateless so you have to provide all the neccessary information in the question.
    
    Args:
        question: The question to ask the ETF expert
    """
    agent = runtime.context.etf_expert_agent
    if not agent:
        raise ValueError("ETF expert agent is not initialized in the runtime context.")

    conversation = [Message(role=MessageRole.USER, content=question)]
    response: ExpertResponse = await agent.generate_response(
        conversation, 
    )

    return response.answer


@tool("cryptoExpert")
async def crypto_expert(runtime: ToolRuntime[ToolRuntimeContext], question: str) -> str:
    """
    This tool provides access to a cryptocurrency expert agent. This is your go to expert in case you want
    information or analysis of cryptocurrencies or any other crypto related questions. 
    This expert has real time data access to the following:
    - Searching for cryptocurrencies
    - Detailed data for specific cryptocurrencies
    - Latest market and cryptocurrency-specific news

    IMPORTANT: The crypto expert is stateless so you have to provide all the neccessary information in the question.
    
    Args:
        question: The question to ask the crypto expert
    """
    agent = runtime.context.crypto_expert_agent
    if not agent:
        raise ValueError("Crypto expert agent is not initialized in the runtime context.")

    conversation = [Message(role=MessageRole.USER, content=question)]
    response: ExpertResponse = await agent.generate_response(
        conversation, 
    )

    return response.answer


@tool("stockAnalystExpert")
async def stock_analyst_expert(runtime: ToolRuntime[ToolRuntimeContext], question: str) -> str:
    """
    This tool provides access to a stock analyst expert agent. This is your go to expert in case you want
    information or deep analysis of a stock or a company. This expert has real time data access to the following:
    - Latest news of the stock
    - Overview of the stock (general information about the company, past performance, etc.)
    - Financials of the company (income statements, balance sheets, cash flows, financial ratios, etc.)
    - Earnings call transcripts
    - Insider transactions
    - KPI metrics
    
    IMPORTANT: The stock analyst expert is stateless so you have to provide all the neccessary information in the question.
    
    Args:
        question: The question to ask the stock analyst expert
    """
    agent = runtime.context.stock_analyst_expert_agent
    if not agent:
        raise ValueError("Stock analyst expert agent is not initialized in the runtime context.")

    conversation = [Message(role=MessageRole.USER, content=question)]
    response: ExpertResponse = await agent.generate_response(
        conversation, 
    )

    return response.answer


@tool("marketAnalystExpert")
async def market_analyst_expert(runtime: ToolRuntime[ToolRuntimeContext], question: str) -> str:
    """
    This tool provides access to a financials market analyst expert agent. This is your go to expert in case you want
    to get the big picture of the market or any other financial markets related questions. 
    This expert has real time data access to the following:
    - Latest market news
    - Stock sectors information (general information about the sectors, past performance, etc.)
    - Economic indicators (inflation, interest rates, unemployment, etc.)
    - Commodities data
    - Investing themes (AI, clean energy, etc.)
    - Access to super investors portfolios (e.g. Warren Buffett, etc.)
    
    
    IMPORTANT: The financial markets analyst expert is stateless so you have to provide all the neccessary information in the question.
    
    Args:
        question: The question to ask the financial markets analyst expert
    """
    agent = runtime.context.financial_markets_analyst_expert_agent
    if not agent:
        raise ValueError("Financial markets analyst expert agent is not initialized in the runtime context.")

    conversation = [Message(role=MessageRole.USER, content=question)]
    response: ExpertResponse = await agent.generate_response(
        conversation, 
    )

    return response.answer


@tool("portfolioManager")
async def portfolio_manager(runtime: ToolRuntime[ToolRuntimeContext], question: str) -> str:
    """
    This tool provides access to your client's portfolio manager agent. This is your go to agent in case you want
    to get information about the client's portfolio or perform actions(place orders) on behalf of the client.
    This agent has access to the following:
    - Client's coinbase account
        - real time balances of the client's portfolio
        - placing buy/sell orders
        - order history
    - Client's alpaca account
        - real time balances of the client's portfolio
        - placing buy/sell orders
        - order history

    IMPORTANT: The portfolio manager is stateless so you have to provide all the neccessary information in the question.
    
    Args:
        question: The question to ask the portfolio manager
    """
    agent = runtime.context.portfolio_manager_agent
    if not agent:
        raise ValueError("Portfolio manager agent is not initialized in the runtime context.")

    conversation = [Message(role=MessageRole.USER, content=question)]
    response: ExpertResponse = await agent.generate_response(
        conversation, 
    )

    return response.answer
