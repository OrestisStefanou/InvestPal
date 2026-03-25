import datetime as dt
from typing import Type

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain.tools import (
    BaseTool,
    tool,
)
from langchain.chat_models import BaseChatModel
from langchain.agents.middleware import AgentMiddleware
from pydantic import (
    BaseModel, 
    Field,
)

from models.session import (
    MessageRole,
    Message,
)
from config import (
    settings,
    LLMProvider,
)
from services.agents.prompts import (
    ETF_EXPERT_PROMPT,
    CRYPTO_EXPERT_PROMPT,
    STOCK_ANALYST_EXPERT_PROMPT,
    MARKET_ANALYST_EXPERT_PROMPT,
    PORTFOLIO_MANAGER_PROMPT,
)


@tool("getCurrentDatetime")
async def get_current_datetime() -> str:
    """
    Get the current datetime.
    """
    return dt.datetime.now().isoformat()


class Agent:
    def __init__(
        self,
        tools: list[BaseTool],
        response_format: Type[ToolStrategy],
        system_prompt: str,
        middleware: list[AgentMiddleware],
        runtime_context_schema: Type[BaseModel] | None = None,
        provider: LLMProvider = LLMProvider.ANTHROPIC,
    ):
        model = self._setup_llm_model(provider)
        self._agent= create_agent(
            model,
            tools=tools + [get_current_datetime],
            response_format=response_format,
            system_prompt=system_prompt,
            middleware=middleware,
            context_schema=runtime_context_schema,
        )

    async def generate_response(
        self,
        conversation: list[Message],
        runtime_context: Type[BaseModel] | None = None,
    ) -> BaseModel:
        messages = []
        # Keep the last settings.CONVERSATION_MESSAGES_LIMIT messages
        if len(conversation) > settings.CONVERSATION_MESSAGES_LIMIT:
            conversation = conversation[-settings.CONVERSATION_MESSAGES_LIMIT:]

        for message in conversation:
            if message.role == MessageRole.USER:
                messages.append({"role": "user", "content": message.content})
            elif message.role == MessageRole.AGENT:
                messages.append({"role": "assistant", "content": message.content})

        response = await self._agent.ainvoke(
            {"messages": messages},
            context=runtime_context,
        )
        return response["structured_response"]

    def _setup_llm_model(self, provider: LLMProvider) -> BaseChatModel:
        match provider:
            case LLMProvider.OPENAI:
                return ChatOpenAI(
                    api_key=settings.OPENAI_API_KEY,
                    model=settings.LLM_MODEL,
                    temperature=settings.TEMPERATURE,
                )
            case LLMProvider.GOOGLE:
                return ChatGoogleGenerativeAI(
                    google_api_key=settings.GOOGLE_API_KEY,
                    model=settings.LLM_MODEL,
                    temperature=settings.TEMPERATURE,
                )
            case LLMProvider.ANTHROPIC:
                return ChatAnthropic(
                    api_key=settings.ANTHROPIC_API_KEY,
                    model=settings.LLM_MODEL,
                    temperature=settings.TEMPERATURE,
                )
            case _:
                raise ValueError(f"Unknown LLM provider: {provider}")


class ExpertResponse(BaseModel):
    answer: str = Field(description="The answer to the user's question.")


class EtfExpertAgent(Agent):
    def __init__(
        self,
        market_data_tools: list[BaseTool],
        middleware: list[AgentMiddleware],
        provider: LLMProvider = LLMProvider.ANTHROPIC,
    ):
        etf_tool_names = [
            "etfSearch",
            "getETF",
            "getMarketNews",
            "getStockOverview",
            "calculateInvestmentFutureValue",
            "stockSearch",
        ]
        etf_tools = [tool for tool in market_data_tools if tool.name in etf_tool_names]
        
        super().__init__(
            tools=etf_tools,
            response_format=ToolStrategy(ExpertResponse),
            system_prompt=ETF_EXPERT_PROMPT,
            middleware=middleware,
            provider=provider,
        )


class CryptoExpertAgent(Agent):
    def __init__(
        self,
        market_data_tools: list[BaseTool],
        middleware: list[AgentMiddleware],
        provider: LLMProvider = LLMProvider.ANTHROPIC,
    ):
        crypto_tool_names = [
            "getMarketNews",
            "searchCryptocurrencies",
            "getCryptocurrencyDataById",
            "getCryptocurrencyNews",
            "calculateInvestmentFutureValue",
        ]
        crypto_tools = [tool for tool in market_data_tools if tool.name in crypto_tool_names]
        
        super().__init__(
            tools=crypto_tools,
            response_format=ToolStrategy(ExpertResponse),
            system_prompt=CRYPTO_EXPERT_PROMPT,
            middleware=middleware,
            provider=provider,
        )


class StockAnalystExpertAgent(Agent):
    def __init__(
        self,
        market_data_tools: list[BaseTool],
        middleware: list[AgentMiddleware],
        provider: LLMProvider = LLMProvider.ANTHROPIC,
    ):
        stock_analyst_tool_names = [
            "stockSearch",
            "getStockOverview",
            "getMarketNews",
            "getStockFinancials",
            "calculateInvestmentFutureValue",
            "getEarningsCallTranscript",
            "getInsiderTransactions",
            "getCompanyKpiMetrics",
        ]
        stock_analyst_tools = [tool for tool in market_data_tools if tool.name in stock_analyst_tool_names]
        
        super().__init__(
            tools=stock_analyst_tools,
            response_format=ToolStrategy(ExpertResponse),
            system_prompt=STOCK_ANALYST_EXPERT_PROMPT,
            middleware=middleware,
            provider=provider,
        )


class MarketAnalystExpertAgent(Agent):
    def __init__(
        self,
        market_data_tools: list[BaseTool],
        middleware: list[AgentMiddleware],
        provider: LLMProvider = LLMProvider.ANTHROPIC,
    ):
        market_analyst_tool_names = [
            "stockSearch",
            "getStockOverview",
            "getMarketNews",
            "getSectors",
            "getSectorStocks",
            "getEconomicIndicatorTimeSeries",
            "getCommodityTimeSeries",
            "getInvestingIdeas",
            "getInvestingIdeaStocks",
            "getSuperInvestors",
            "getSuperInvestorPortfolio",
        ]
        market_analyst_tools = [tool for tool in market_data_tools if tool.name in market_analyst_tool_names]
        
        super().__init__(
            tools=market_analyst_tools,
            response_format=ToolStrategy(ExpertResponse),
            system_prompt=MARKET_ANALYST_EXPERT_PROMPT,
            middleware=middleware,
            provider=provider,
        )


class PortfolioManagerAgent(Agent):
    def __init__(
        self,
        portfolio_management_tools: list[BaseTool],
        middleware: list[AgentMiddleware],
        provider: LLMProvider = LLMProvider.ANTHROPIC,
    ):
        super().__init__(
            tools=portfolio_management_tools,
            response_format=ToolStrategy(ExpertResponse),
            system_prompt=PORTFOLIO_MANAGER_PROMPT,
            middleware=middleware,
            provider=provider,
        )