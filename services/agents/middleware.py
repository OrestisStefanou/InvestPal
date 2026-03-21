import logging

from langchain.agents.middleware import AgentMiddleware
from langchain.messages import ToolMessage

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
