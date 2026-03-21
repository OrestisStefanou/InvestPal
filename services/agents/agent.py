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
from config import settings


class Agent:
    def __init__(
            self,
            tools: list[BaseTool],
            model: BaseChatModel,
            response_format: Type[ToolStrategy],
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
