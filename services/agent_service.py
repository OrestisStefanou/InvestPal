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
from services.user_context import (
    UserContextService, 
    UserContextNotFoundError,
)
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

# TODO: This should be removed after we deprecate the old InvestmentAdvisorAgentService
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


class TextAgentService(ABC):
    @abstractmethod
    async def generate_agent_text_response(
        self,
        user_id: str, 
        conversation: list[Message],
    ) -> str:
        pass


class InvestmentManagerAgentService(TextAgentService):
    """
    Service that orchestrates the investment management interaction by coordinating multiple agents.

    This service is responsible for:
    1. Fetching the user's current context (profile).
    2. Invoking the InvestmentManagerAgent to generate a personalized response based on the 
       conversation history and the user's profile.
    3. Invoking the UserContextMemoryManagerAgent in parallel to update and persist any new 
       information about the user revealed during the conversation.

    It acts as the high-level coordinator that ensures both response generation and context 
    management happen seamlessly.
    """

    def __init__(
        self, 
        investment_manager_agent: InvestmentManagerAgent,
        user_context_memory_manager_agent: UserContextMemoryManagerAgent,
        user_context_service: UserContextService,
    ):
        """
        Initializes the InvestmentManagerAgentService.

        Args:
            investment_manager_agent: The agent responsible for providing investment advice.
            user_context_memory_manager_agent: The agent responsible for updating user context.
            user_context_service: Service to retrieve and store user context.
        """
        self._investment_manager_agent = investment_manager_agent
        self._user_context_memory_manager_agent = user_context_memory_manager_agent
        self._user_context_service = user_context_service
    
    async def generate_agent_text_response(
        self,
        user_id: str, 
        conversation: list[Message],
    ) -> str:
        """
        Generates a response from the investment manager agent and updates user context.

        Args:
            user_id: The unique identifier of the user.
            conversation: The list of messages in the current conversation.

        Returns:
            InvestmentManagerAgentResponse: The response generated by the investment manager.

        Raises:
            UserContextNotFoundError: If the user context cannot be found.
        """
        user_context = await self._user_context_service.get_user_context(user_id)
        if not user_context:
            raise UserContextNotFoundError()
        
        # Generate the response from the investment manager agent
        agent_response = await self._investment_manager_agent.generate_response(
            conversation=conversation,
            system_prompt_placeholder_values=InvestmentManagerPromptVars(
                client_profile=user_context.model_dump(),
            )
        )

        # Update the user context memory
        await self._user_context_memory_manager_agent.generate_response(
            conversation=conversation,
            system_prompt_placeholder_values=UserContextMemoryManagerPromptVars(
                user_id=user_id,
            ),
            runtime_context=UserContextManagerRuntimeContext(
                user_context_service=self._user_context_service,
            ),
        )

        return agent_response.response
