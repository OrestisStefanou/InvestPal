from typing import (
    Any,
    Type, 
    TypedDict,
    Mapping,
)
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from langchain.tools import BaseTool
from langchain.chat_models import BaseChatModel
from langchain.agents.middleware import AgentMiddleware
from pydantic import BaseModel
from langchain_mcp_adapters.client import MultiServerMCPClient

from models.session import (
    MessageRole,
    Message,
)
from config import (
    settings,
    LLMProvider,
)
from services.agents.prompts import (
    INVESTMENT_MANAGER_AGENT_PROMPT,
    USER_CONTEXT_MEMORY_MANAGER_PROMPT,
)
from services.agents.tools import (
    UserContextToolsRuntimeContext,
    update_user_context,
    get_user_context,
    get_current_datetime,
    get_user_conversation_notes,
    update_user_conversation_notes,
)

# TODO: Create Agent ABC clas 


class Agent:
    def __init__(
        self,
        tools: list[BaseTool],
        response_format: Type[BaseModel],
        system_prompt: str,
        middleware: list[AgentMiddleware],
        runtime_context_schema: Type[Any] | None = None,
        provider: LLMProvider = LLMProvider.ANTHROPIC,
        model_name: str = settings.LLM_MODEL,
        temperature: float = settings.TEMPERATURE,
    ):
        self.tools = tools
        self.response_format = response_format
        self.system_prompt = system_prompt
        self.middleware = middleware
        self.runtime_context_schema = runtime_context_schema
        self.provider = provider
        self.model_name = model_name
        self.temperature = temperature

    async def generate_response(
        self,
        conversation: list[Message],
        runtime_context: Any | None = None,
        system_prompt_placeholder_values: Mapping[str, Any] | None = None,
    ) -> BaseModel:
        agent = self._setup_agent(system_prompt_placeholder_values)
        messages = []
        # Keep the last settings.CONVERSATION_MESSAGES_LIMIT messages
        if len(conversation) > settings.CONVERSATION_MESSAGES_LIMIT:
            conversation = conversation[-settings.CONVERSATION_MESSAGES_LIMIT:]

        for message in conversation:
            if message.role == MessageRole.USER:
                messages.append({"role": "user", "content": message.content})
            elif message.role == MessageRole.AGENT:
                messages.append({"role": "assistant", "content": message.content})

        response = await agent.ainvoke(
            {"messages": messages},
            context=runtime_context,
        )

        return response["structured_response"]

    def _setup_agent(self, system_prompt_placeholder_values: Mapping[str, Any] | None = None):
        model = self._setup_llm_model(self.provider, self.model_name, self.temperature)

        system_prompt = self.system_prompt
        if system_prompt_placeholder_values:
            system_prompt = system_prompt.format(**system_prompt_placeholder_values)

        return create_agent(
            model=model,
            tools=self.tools,
            response_format=self.response_format,
            system_prompt=system_prompt,
            middleware=self.middleware,
            context_schema=self.runtime_context_schema,
        )

    def _setup_llm_model(self, provider: LLMProvider, model_name: str, temperature: float) -> BaseChatModel:
        match provider:
            case LLMProvider.OPENAI:
                return ChatOpenAI(
                    api_key=settings.OPENAI_API_KEY,
                    model=model_name,
                    temperature=temperature,
                )
            case LLMProvider.GOOGLE:
                return ChatGoogleGenerativeAI(
                    google_api_key=settings.GOOGLE_API_KEY,
                    model=model_name,
                    temperature=temperature,
                )
            case LLMProvider.ANTHROPIC:
                return ChatAnthropic(
                    api_key=settings.ANTHROPIC_API_KEY,
                    model=model_name,
                    temperature=temperature,
                )
            case _:
                raise ValueError(f"Unknown LLM provider: {provider}")


class InvestmentManagerAgentResponse(BaseModel):
    """
    Schema for the structured response from the Investment Manager Agent.
    """
    response: str


class InvestmentManagerPromptVars(TypedDict):
    """
    Schema for placeholder values required by the Investment Manager Agent's system prompt.

    Attributes:
        client_profile: A dictionary containing the user's investment profile and context.
    """
    client_profile: dict[str, Any]


@dataclass
class UserContextManagerRuntimeContext(UserContextToolsRuntimeContext):
    pass


class InvestmentManagerAgent(Agent):
    """
    Agent responsible for providing personalized investment management guidance.
    Note: Callers should use the create method to create an instance of this agent.
    """
    def __init__(
        self,
        tools: list[BaseTool],
        middleware: list[AgentMiddleware],
    ):
        """
        Initializes the Investment Manager Agent with the configured LLM settings.

        Args:
            tools: List of tools available to the agent.
            middleware: List of middleware to process agent actions and responses.
        """
        super().__init__(
            tools=tools,
            response_format=InvestmentManagerAgentResponse,
            system_prompt=INVESTMENT_MANAGER_AGENT_PROMPT,
            middleware=middleware,
            runtime_context_schema=UserContextManagerRuntimeContext,
            provider=settings.INVESTMENT_MANAGER_LLM_PROVIDER,
            model_name=settings.INVESTMENT_MANAGER_LLM_MODEL,
            temperature=settings.INVESTMENT_MANAGER_TEMPERATURE,
        )

    async def generate_response(
        self,
        conversation: list[Message],
        runtime_context: Any | None = None,
        system_prompt_placeholder_values: InvestmentManagerPromptVars | None = None,
    ) -> InvestmentManagerAgentResponse:
        """
        Generates a response using the Investment Manager's specific prompt requirements.
        """
        return await super().generate_response(
            conversation=conversation,
            runtime_context=runtime_context,
            system_prompt_placeholder_values=system_prompt_placeholder_values,
        )

    @classmethod
    async def create(
        cls,
        mcp_client: MultiServerMCPClient,
        middleware: list[AgentMiddleware],
    ):
        tools = [get_current_datetime, get_user_conversation_notes]
        if settings.MARKET_DATA_MCP_SERVER_URL:
            market_data_tools = await mcp_client.get_tools(server_name=settings.MARKET_DATA_MCP_SERVER_NAME)
            tools.extend(market_data_tools)

        if settings.ALPACA_MCP_SERVER_URL:
            alpaca_tools = await mcp_client.get_tools(server_name=settings.ALPACA_MCP_SERVER_NAME)
            tools.extend(alpaca_tools)
        
        if settings.COINBASE_MCP_SERVER_URL:
            coinbase_tools = await mcp_client.get_tools(server_name=settings.COINBASE_MCP_SERVER_NAME)
            tools.extend(coinbase_tools)

        return cls(tools=tools, middleware=middleware)


class UserContextMemoryManagerAgentResponse(BaseModel):
    """
    Schema for the structured response from the User Context Memory Manager Agent.
    """
    response: str


class UserContextMemoryManagerPromptVars(TypedDict):
    """
    Schema for placeholder values required by the User Context Memory Manager Agent's system prompt.

    Attributes:
        user_id: The ID of the user to manage context for.
    """
    user_id: str


class UserContextMemoryManagerAgent(Agent):
    """
    Agent responsible for managing the user context memory.
    """
    def __init__(
        self,
        middleware: list[AgentMiddleware],
    ):
        tools = [
            update_user_context,
            get_user_context,
            get_current_datetime,
            get_user_conversation_notes,
            update_user_conversation_notes,
        ]
        super().__init__(
            tools=tools,
            response_format=UserContextMemoryManagerAgentResponse,
            system_prompt=USER_CONTEXT_MEMORY_MANAGER_PROMPT,
            middleware=middleware,
            runtime_context_schema=UserContextManagerRuntimeContext,   # TODO: We need a custom class for this agent runtime context
            provider=settings.USER_CONTEXT_MEMORY_MANAGER_LLM_PROVIDER,
            model_name=settings.USER_CONTEXT_MEMORY_MANAGER_LLM_MODEL,
            temperature=settings.USER_CONTEXT_MEMORY_MANAGER_TEMPERATURE,
        )

    async def generate_response(
        self,
        conversation: list[Message],
        runtime_context: UserContextManagerRuntimeContext | None = None,
        system_prompt_placeholder_values: UserContextMemoryManagerPromptVars | None = None,
    ) -> UserContextMemoryManagerAgentResponse:
        return await super().generate_response(
            conversation=conversation,
            runtime_context=runtime_context,
            system_prompt_placeholder_values=system_prompt_placeholder_values,
        )
