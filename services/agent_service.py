import logging
from typing import Type
from abc import (
    ABC,
    abstractmethod,
)

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents.structured_output import ToolStrategy
from pydantic import BaseModel

from models.session import Message
from config import (
    settings,
)
from services.user_context import UserContextService
from services.agents.prompts import (
    INVESTMENT_ADVISOR_PROMPT,
    INVESTMENT_MANAGER_PROMPT,
)
from services.agents.middleware import (
    ToolErrorMiddleware,
    ToolLoggingMiddleware,
)
from services.agents.tools import (
    ToolRuntimeContext,
    update_user_context,
    get_user_context,
    etf_expert,
    crypto_expert,
    stock_analyst_expert,
    market_analyst_expert,
    portfolio_manager,
)
from services.agents.agent import (
    Agent,
    EtfExpertAgent,
    CryptoExpertAgent,
    StockAnalystExpertAgent,
    MarketAnalystExpertAgent,
    PortfolioManagerAgent,
)

logger = logging.getLogger(__name__)


class TextResponseFormat(BaseModel):
    response: str


class AgentService(ABC):
    @abstractmethod
    async def generate_response(
        self,
        user_id: str, 
        conversation: list[Message],
        response_format: type[BaseModel],
    ) -> BaseModel:
        pass


class InvestmentAdvisorAgentService(AgentService):
    def __init__(
        self, 
        mcp_client: MultiServerMCPClient,
        user_context_service: UserContextService,
    ):
        self._mcp_client = mcp_client
        self._user_context_service = user_context_service

    async def generate_response(
        self,
        user_id: str, 
        conversation: list[Message],
        response_format: Type[BaseModel],
    ) -> BaseModel:
        system_prompt = self._get_system_prompt(user_id)
        agent = await self._create_agent(system_prompt, response_format)
        runtime_context = ToolRuntimeContext(
            user_context_service=self._user_context_service,
            etf_expert_agent=None,
            crypto_expert_agent=None,
            stock_analyst_expert_agent=None,
            market_analyst_expert_agent=None,
            portfolio_manager_agent=None,
        )
        response = await agent.generate_response(conversation, runtime_context)
        return response

    def _get_system_prompt(self, user_id: str) -> str:
        return INVESTMENT_ADVISOR_PROMPT.format(user_id=user_id)

    async def _create_agent(self, system_prompt: str, response_format: BaseModel) -> Agent:
        mcp_tools = await self._mcp_client.get_tools()
        internal_tools = [
            update_user_context,
            get_user_context
        ]
        tools = mcp_tools + internal_tools

        return Agent(
            tools=tools,
            response_format=ToolStrategy(response_format),
            system_prompt=system_prompt,
            middleware=[ToolErrorMiddleware(), ToolLoggingMiddleware()],
            runtime_context_schema=ToolRuntimeContext,
        )


class InvestmentManagerMultiAgentService(AgentService):
    def __init__(
        self,
        user_context_service: UserContextService,
        etf_expert_agent: EtfExpertAgent,
        crypto_expert_agent: CryptoExpertAgent,
        stock_analyst_expert_agent: StockAnalystExpertAgent,
        market_analyst_expert_agent: MarketAnalystExpertAgent,
        portfolio_manager_agent: PortfolioManagerAgent,
    ):
        self._user_context_service = user_context_service   # todo: probably not needed
        self._etf_expert_agent = etf_expert_agent
        self._crypto_expert_agent = crypto_expert_agent
        self._stock_analyst_expert_agent = stock_analyst_expert_agent
        self._market_analyst_expert_agent = market_analyst_expert_agent
        self._portfolio_manager_agent = portfolio_manager_agent

    async def generate_response(
        self,
        user_id: str, 
        conversation: list[Message],
        response_format: Type[BaseModel],
    ) -> BaseModel:
        system_prompt = INVESTMENT_MANAGER_PROMPT.format(client_profile={"name": "Orestis"})
        agent = await self._create_agent(system_prompt, response_format)
        runtime_context = ToolRuntimeContext(
            user_context_service=self._user_context_service,
            etf_expert_agent=self._etf_expert_agent,
            crypto_expert_agent=self._crypto_expert_agent,
            stock_analyst_expert_agent=self._stock_analyst_expert_agent,
            market_analyst_expert_agent=self._market_analyst_expert_agent,
            portfolio_manager_agent=self._portfolio_manager_agent,
        )
        response = await agent.generate_response(conversation, runtime_context)
        return response

    async def _create_agent(self, system_prompt: str, response_format: BaseModel) -> Agent:
        return Agent(
            tools=[
                etf_expert,
                crypto_expert,
                stock_analyst_expert,
                market_analyst_expert,
                portfolio_manager
            ],
            response_format=ToolStrategy(response_format),
            system_prompt=system_prompt,
            middleware=[ToolErrorMiddleware(), ToolLoggingMiddleware()],
            runtime_context_schema=ToolRuntimeContext,
        )
