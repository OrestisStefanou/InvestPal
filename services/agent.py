import logging
from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import Type

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents.structured_output import ToolStrategy
from langchain.tools import (
    BaseTool,
    tool,
    ToolRuntime,
)
from langchain.chat_models import BaseChatModel
from langchain.agents.middleware import AgentMiddleware
from langchain.messages import ToolMessage
from langchain_anthropic import ChatAnthropic
from pydantic import (
    BaseModel,
    Field,
)

from models.session import (
    MessageRole,
    Message,
)
from models.user_context import (
    UserContext,
    UserPortfolioHolding
)
from config import (
    settings,
    LLMProvider,
)
from services.user_context import UserContextService
from services.prompts import INVESTMENT_ADVISOR_PROMPT

logger = logging.getLogger(__name__)


class ToolErrorMiddleware(AgentMiddleware):
    async def awrap_tool_call(self, request, handler):
        try:
            return await handler(request)
        except Exception as e:
            logger.exception("ERROR IN TOOL CALL: %s", str(e))
            return ToolMessage(
                content=f"Tool error: ({str(e)})",
                tool_call_id=request.tool_call["id"],
            )


class ToolLoggingMiddleware(AgentMiddleware):
    async def awrap_tool_call(self, request, handler):
        tool_name = request.tool_call["name"]
        tool_input = request.tool_call["args"]
        logger.info("CALLING TOOL [%s] WITH INPUT: %s", tool_name, tool_input)
        
        result = await handler(request)
        
        logger.info("TOOL [%s] RESULT: %s", tool_name, result.content if hasattr(result, "content") else result)
        return result


@dataclass
class ToolRuntimeContext:
    user_context_service: UserContextService


class TextResponseFormat(BaseModel):
    response: str


class Agent:
    def __init__(
        self, 
        tools: list[BaseTool],
        model: BaseChatModel,
        response_format: ToolStrategy,
        system_prompt: str,
        middleware: list[AgentMiddleware],
        runtime_context_schema: Type[BaseModel],
    ):
        self._agent= create_agent(
            model, 
            tools=tools,
            response_format=response_format,
            system_prompt=system_prompt,
            middleware=middleware,
            context_schema=runtime_context_schema,
        )
    
    async def generate_response(
        self, 
        conversation: list[Message],
        runtime_context: BaseModel,
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
        response_format: BaseModel,
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
            get_user_context
        ]
        tools = mcp_tools + internal_tools
        match settings.LLM_PROVIDER:
            case LLMProvider.OPENAI:
                model = ChatOpenAI(
                    api_key=settings.OPENAI_API_KEY,
                    model=settings.LLM_MODEL,
                    temperature=settings.TEMPERATURE,
                )
            case LLMProvider.GOOGLE:
                model = ChatGoogleGenerativeAI(
                    google_api_key=settings.GOOGLE_API_KEY,
                    model=settings.LLM_MODEL,
                    temperature=settings.TEMPERATURE,
                )
            case LLMProvider.ANTHROPIC:
                model = ChatAnthropic(
                    api_key=settings.ANTHROPIC_API_KEY,
                    model=settings.LLM_MODEL,
                    temperature=settings.TEMPERATURE,
                )
            case _:
                raise ValueError(f"Unknown LLM provider: {settings.LLM_PROVIDER}") 

        return Agent(
            tools=tools,
            model=model,
            response_format=ToolStrategy(response_format),
            system_prompt=system_prompt,
            middleware=[ToolErrorMiddleware(), ToolLoggingMiddleware()],
            runtime_context_schema=ToolRuntimeContext,
        )


## User context tools
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
async def get_user_context(runtime: ToolRuntime[ToolRuntimeContext],user_id: str) -> UserContext:
    """Get the user context including user profile and portfolio holdings.

    Args:
        user_id: The id of the user to get the context for
    """
    user_context_service = runtime.context.user_context_service
    user_context = await user_context_service.get_user_context(user_id)
    return user_context
