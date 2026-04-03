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
from services.agents.prompts import INVESTMENT_ADVISOR_PROMPT
from models.user_context import (
    UserContext,
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
    description="Update the user context(for the given user_id) including user profile. Note: The provided context will completely replace the existing one, so the entire updated object must be provided.",
)
async def update_user_context(
    user_id: Annotated[str, "The id of the user to update the context for"],
    user_profile: Annotated[dict, "General information about the user. Must provide the complete user profile as it will replace the existing one."],
    user_context_service: UserContextService = Depends(get_user_context_service),
) -> UserContext:
    updated_user_context = await user_context_service.update_user_context(
        user_id=user_id,
        user_profile=user_profile,
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


@mcp_app.tool(
    name="getUserConversationNotes",
    description=(
        "Retrieve conversation notes for a user, optionally filtered by date. "
        "Each entry in the returned list maps a date (YYYY-MM-DD) to its notes dict. "
        "Always call this before updateUserConversationNotes to avoid storing duplicate information."
    ),
)
async def get_user_conversation_notes(
    user_id: Annotated[str, "The id of the user to get conversation notes for"],
    date: Annotated[str | None, "Optional date filter in YYYY-MM-DD format. If omitted, returns notes for all dates."] = None,
    user_context_service: UserContextService = Depends(get_user_context_service),
) -> list[dict]:
    return await user_context_service.get_user_conversation_notes(user_id=user_id, date=date)


@mcp_app.tool(
    name="updateUserConversationNotes",
    description=(
        "Store or update conversation notes for a specific user and date. "
        "Notes will completely replace existing notes for that date, so merge with existing notes "
        "retrieved via getUserConversationNotes first. "
        "Keep notes short and concise — focused on information useful for future investment advice."
    ),
)
async def update_user_conversation_notes(
    user_id: Annotated[str, "The id of the user to update conversation notes for"],
    date: Annotated[str, "The date of the conversation in YYYY-MM-DD format"],
    notes: Annotated[dict, "A key-value store of short, concise notes about the conversation on this date"],
    user_context_service: UserContextService = Depends(get_user_context_service),
) -> None:
    await user_context_service.update_user_conversation_notes(
        user_id=user_id,
        date=date,
        notes=notes,
    )


@mcp_app.prompt
def get_invstment_advisor_prompt(user_id: str) -> str:
    return INVESTMENT_ADVISOR_PROMPT.format(user_id=user_id)

if __name__ == "__main__":
    mcp_app.run(transport="http", port=9000)