import logging
from typing import Annotated

from fastmcp import FastMCP
from fastmcp.server.lifespan import lifespan
from fastmcp.dependencies import (
    Depends,
    CurrentContext,
)
from fastmcp.server.context import Context
from fastmcp.server.middleware import (
    Middleware,
    MiddlewareContext,
)
from pymongo import AsyncMongoClient

from config import settings
from services.user_context import (
    MongoDBUserContextService,
    UserContextService,
)
from services.prompts import INVESTMENT_ADVISOR_PROMPT
from models.user_context import (
    UserContext,
    UserPortfolioHolding
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class LoggingMiddleware(Middleware):
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        tool_name = context.message.name
        args = context.message.arguments
        logger.info("Calling tool %s with arguments %s", tool_name, args)
        result = await call_next(context)
        logger.info("Tool call %s with arguments %s returned result %s", tool_name, args, result)
        return result


@lifespan
async def db_lifespan(server):
    db_client = AsyncMongoClient(settings.MONGO_URI)
    yield {"db_client": db_client}
    await db_client.close()


def get_user_context_service(ctx: Context = CurrentContext()) -> UserContextService:
    db_client = ctx.lifespan_context["db_client"]
    return MongoDBUserContextService(mongo_client=db_client)


mcp_app = FastMCP("InvestPal MCP Server", lifespan=db_lifespan)
mcp_app.add_middleware(LoggingMiddleware())


@mcp_app.tool(
    name="updateUserContext",
    description="Update the user context(for the given user_id) including user profile and portfolio holdings. Note: The provided context will completely replace the existing one, so the entire updated object must be provided.",
)
async def update_user_context(
    user_id: Annotated[str, "The id of the user to update the context for"],
    user_profile: Annotated[dict, "General information about the user. Must provide the complete user profile as it will replace the existing one."],
    user_portfolio: Annotated[list[UserPortfolioHolding], "List of portfolio holdings. Must provide the complete portfolio as it will replace the existing one."],
    user_context_service: UserContextService = Depends(get_user_context_service),
) -> UserContext:
    updated_user_context = await user_context_service.update_user_context(
        user_id=user_id,
        user_profile=user_profile,
        user_portfolio=user_portfolio,
    )

    return updated_user_context


@mcp_app.tool(
    name="getUserContext",
    description="Get the user context(for the given user_id) including user profile and portfolio holdings.",
)
async def update_user_context(
    user_id: Annotated[str, "The id of the user to get the context for"],
    user_context_service: UserContextService = Depends(get_user_context_service),
) -> UserContext:
    user_context = await user_context_service.get_user_context(user_id=user_id)
    return user_context


@mcp_app.prompt
def get_invstment_advisor_prompt(user_id: str) -> str:
    return INVESTMENT_ADVISOR_PROMPT.format(user_id=user_id)

if __name__ == "__main__":
    mcp_app.run(transport="http", port=9000)