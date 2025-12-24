from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents.structured_output import ToolStrategy
from langchain.tools import BaseTool
from langchain.chat_models import BaseChatModel
from langchain.agents.middleware import AgentMiddleware
from langchain.messages import ToolMessage
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel

from services.session import (
    MessageRole,
    Message,
)
from config import (
    settings,
    LLMProvider,
)

class ToolErrorMiddleware(AgentMiddleware):
    async def awrap_tool_call(self, request, handler):
        try:
            return await handler(request)
        except Exception as e:
            return ToolMessage(
                content=f"Tool error: ({str(e)})",
                tool_call_id=request.tool_call["id"],
            )


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
    ):
        self._agent= create_agent(
            model, 
            tools=tools,
            response_format=response_format,
            system_prompt=system_prompt,
            middleware=middleware,
        )
    
    async def generate_response(self, conversation: list[Message]) -> str:
        messages = []
        # Keep the last settings.CONVERSATION_MESSAGES_LIMIT messages
        if len(conversation) > settings.CONVERSATION_MESSAGES_LIMIT:
            conversation = conversation[-settings.CONVERSATION_MESSAGES_LIMIT:] 
        
        for message in conversation:
            if message.role == MessageRole.USER:
                messages.append({"role": "user", "content": message.content})
            elif message.role == MessageRole.AGENT:
                messages.append({"role": "assistant", "content": message.content})
        
        response = await self._agent.ainvoke({"messages": messages})
        return response["structured_response"].response


class AgentService:
    def __init__(
        self, 
        mcp_client: MultiServerMCPClient, 
    ):
        self._mcp_client = mcp_client

    async def generate_response(
        self,
        user_id: str, 
        conversation: list[Message],
        response_format: BaseModel,
    ) -> str:
        system_prompt = await self._get_system_prompt(user_id)
        agent = await self._create_agent(system_prompt, response_format)
        response = await agent.generate_response(conversation)
        return response

    async def _get_system_prompt(self, user_id: str) -> str:
        result = await self._mcp_client.get_prompt(
            server_name=settings.MCP_SERVER_NAME,
            prompt_name="investment_advisor_prompt", 
            arguments={
                'user_id': user_id,
            }
        )
        return result[0].content

    async def _create_agent(self, system_prompt: str, response_format: BaseModel) -> Agent:
        tools = await self._mcp_client.get_tools()
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
            middleware=[ToolErrorMiddleware()],
        )
