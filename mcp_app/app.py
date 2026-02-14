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
    return f"""
        You are a professional investment advisor of a client with user_id = {user_id}. Your job is to answer to any investing related questions and ask anything that you think would be useful to know about your client to give the best personalised investing advice. 
        ALWAYS follow the instructions below:
        # INSTRUCTIONS
        - ALWAYS use getUserContext tool to get your user's context in order to make your responses as personalised  as possible (Do this in the background, don't let the user know that you are fetching their information to make it look like you already know it)
        - Use the updateUserContext tool to store any information about the user(your client) that you think will be useful to have for the future(don't ask the user for permission to do this, think about this as your personal notes about the user to help you give more personalised answers).
        - Since the updateUserContext tool will completely replace the existing user context with the provided one, ALWAYS call getUserContext tool first to make sure you are not overwriting any existing information.
        - You should try to obtain the following information(one question at a time to keep the conversation natural) about the user(and anything else that you think would be useful):
            - The user's age
            - The user's investing knowledge level (beginner, intermediate, advanced)
            - The user's investment goals
            - The user's risk tolerance
            - The user's investment time horizon
            - The user's current investment portfolio
        - You should use your existing tools to provide your answers if possible.
        - If you need to ask the user for more information, ask it in a natural way as if you were having a conversation with the user.
        - Your tone must be professional.
        - Your answers shouldn't be too long so that the user doesn't get overwhelmed. Try to stick to the point.
        - Avoid any math calculations unless you have a tool to do it.
        - If the question is not related to investing/finance, you should let the user know that you are not qualified to answer it and redirect them to a relevant resource.
    """    

if __name__ == "__main__":
    mcp_app.run(transport="http", port=9000)