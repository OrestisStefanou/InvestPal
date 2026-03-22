from typing import Type

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain.tools import BaseTool
from langchain.chat_models import BaseChatModel
from langchain.agents.middleware import AgentMiddleware
from pydantic import BaseModel

from models.session import (
    MessageRole,
    Message,
)
from config import (
    settings,
    LLMProvider,
)
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic


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
            tools=tools,
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
