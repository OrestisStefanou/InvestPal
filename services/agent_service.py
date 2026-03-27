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
from config import settings
from services.user_context import UserContextService
from services.agents.prompts import INVESTMENT_ADVISOR_PROMPT
from services.agents.middleware import (
    ToolErrorMiddleware,
    ToolLoggingMiddleware,
)
from services.agents.tools import (
    ToolRuntimeContext,
    update_user_context,
    get_user_context,
    get_current_datetime,
)
from services.agents.agent import (
    Agent,
    InvestmentManagerAgent,
    InvestmentManagerPromptVars,
    InvestmentManagerAgentResponse,
    UserContextMemoryManagerAgent,
    UserContextMemoryManagerPromptVars,
    UserContextManagerRuntimeContext,
)

logger = logging.getLogger(__name__)

# TODO: This should be removed
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
        )
        response = await agent.generate_response(conversation, runtime_context)
        return response

    def _get_system_prompt(self, user_id: str) -> str:
        return INVESTMENT_ADVISOR_PROMPT.format(user_id=user_id)

    async def _create_agent(self, system_prompt: str, response_format: BaseModel) -> Agent:
        mcp_tools = await self._mcp_client.get_tools()
        internal_tools = [
            update_user_context,
            get_user_context,
            get_current_datetime,
        ]
        tools = mcp_tools + internal_tools

        return Agent(
            tools=tools,
            response_format=ToolStrategy(response_format),
            system_prompt=system_prompt,
            middleware=[ToolErrorMiddleware(), ToolLoggingMiddleware()],
            runtime_context_schema=ToolRuntimeContext,
        )


# TODO: This should replace the existing one
class AgentServiceV2(ABC):
    @abstractmethod
    async def generate_response(
        self,
        user_id: str, 
        conversation: list[Message],
    ) -> BaseModel:
        pass


class InvestmentManagerAgentService(AgentService):
    def __init__(
        self, 
        investment_manager_agent: InvestmentManagerAgent,
        user_context_memory_manager_agent: UserContextMemoryManagerAgent,
        user_context_service: UserContextService,
    ):
        self._investment_manager_agent = investment_manager_agent
        self._user_context_memory_manager_agent = user_context_memory_manager_agent
        self._user_context_service = user_context_service
    
    async def generate_response(
        self,
        user_id: str, 
        conversation: list[Message],
    ) -> InvestmentManagerAgentResponse:
        pass
