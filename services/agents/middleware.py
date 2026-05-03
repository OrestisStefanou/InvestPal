import asyncio
from collections.abc import Callable
import logging

from langchain.agents.middleware import AgentMiddleware
from langchain.messages import ToolMessage
from langchain.tools.tool_node import ToolCallRequest
from langgraph.types import Command


from config import settings

logger = logging.getLogger(__name__)


class ToolErrorMiddleware(AgentMiddleware):
    async def awrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
    ) -> ToolMessage | Command:
        try:
            return await handler(request)
        except Exception as e:
            logger.exception("ERROR IN TOOL CALL: %s", str(e))
            return ToolMessage(
                content=f"Tool error: ({str(e)})",
                tool_call_id=request.tool_call["id"],
            )


class ToolLoggingMiddleware(AgentMiddleware):
    async def awrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
    ) -> ToolMessage | Command:
        tool_name = request.tool_call["name"]
        tool_input = request.tool_call["args"]
        logger.info("CALLING TOOL [%s] WITH INPUT: %s", tool_name, tool_input)

        result = await handler(request)

        logger.info("TOOL [%s] RESULT: %s", tool_name, result.content if hasattr(result, "content") else result)
        return result


class ToolTokenRateLimitMiddleware(AgentMiddleware):
    """
    We have some tools that consume a lot of tokens and this has a
    result to get token rate limit by the LLM provider. The purpose of
    this middleware is to delay the tool execution of the tools that
    consume a big amount of tokens to avoid getting rate limited.

    A class-level lock serialises all token-intensive calls so that when
    the LLM requests multiple such tools in one response (LangGraph runs
    them concurrently via asyncio.gather), they still execute one at a
    time with the full cooldown between them.
    """
    _lock: asyncio.Lock = asyncio.Lock()

    async def awrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
    ) -> ToolMessage | Command:
        tool_name = request.tool_call["name"]
        async with ToolTokenRateLimitMiddleware._lock:
            if tool_name in settings.TOKEN_INTENSIVE_TOOLS:
                await asyncio.sleep(125)
            else:
                await asyncio.sleep(65)

        return await handler(request)
