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
from services.agent_reminder import (
    MongoDBAgentReminderService,
    AgentReminderService,
)
from services.agents.prompts import INVESTMENT_ADVISOR_PROMPT
from models.user_context import (
    UserContext,
    UserConversationNotes,
)
from models.agent_reminder import AgentReminder


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


def get_agent_reminder_service(ctx: Context = CurrentContext()) -> AgentReminderService:
    db_client = ctx.lifespan_context["db_client"]
    return MongoDBAgentReminderService(mongo_client=db_client)


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
        "Allows the agent to recall specific details from past conversations."
    ),
)
async def get_user_conversation_notes(
    user_id: Annotated[str, "The id of the user to get conversation notes for"],
    date: Annotated[str | None, "Optional date filter in YYYY-MM-DD format. If omitted, returns notes for all dates."] = None,
    user_context_service: UserContextService = Depends(get_user_context_service),
) -> list[UserConversationNotes]:
    return await user_context_service.get_user_conversation_notes(user_id=user_id, date=date)


@mcp_app.tool(
    name="updateUserConversationNotes",
    description=(
        "Store or update conversation notes for a specific user and date. "
        "The provided notes will be MERGED with existing ones for that date (only keys "
        "provided will be overwritten or added). Keep notes short and concise."
    ),
)
async def update_user_conversation_notes(
    user_id: Annotated[str, "The id of the user to update conversation notes for"],
    date: Annotated[str, "The date of the conversation in YYYY-MM-DD format"],
    notes: Annotated[dict, "A key-value store of notes about the conversation. These will be merged with any existing notes for this date"],
    user_context_service: UserContextService = Depends(get_user_context_service),
) -> None:
    await user_context_service.update_user_conversation_notes(
        user_id=user_id,
        date=date,
        notes=notes,
    )


@mcp_app.tool(
    name="createAgentReminder",
    description="Create a new reminder for the user.",
)
async def create_agent_reminder(
    user_id: Annotated[str, "The id of the user to create the reminder for"],
    reminder_description: Annotated[str, "The description of the reminder"],
    due_date: Annotated[str | None, "Optional due date for the reminder in YYYY-MM-DD format"] = None,
    agent_reminder_service: AgentReminderService = Depends(get_agent_reminder_service),
) -> AgentReminder:
    return await agent_reminder_service.create_agent_reminder(
        user_id=user_id,
        reminder_description=reminder_description,
        due_date=due_date,
    )


@mcp_app.tool(
    name="getAgentReminders",
    description="Get all reminders for the given user.",
)
async def get_agent_reminders(
    user_id: Annotated[str, "The id of the user to get reminders for"],
    agent_reminder_service: AgentReminderService = Depends(get_agent_reminder_service),
) -> list[AgentReminder]:
    return await agent_reminder_service.get_agent_reminders(user_id=user_id)


@mcp_app.tool(
    name="updateAgentReminder",
    description="Update an existing reminder for the user.",
)
async def update_agent_reminder(
    user_id: Annotated[str, "The id of the user the reminder belongs to"],
    reminder_id: Annotated[str, "The unique id of the reminder to update"],
    reminder_description: Annotated[str | None, "New description for the reminder. If omitted, the existing description is kept."] = None,
    due_date: Annotated[str | None, "New due date for the reminder in YYYY-MM-DD format. If omitted, the existing due date is kept."] = None,
    agent_reminder_service: AgentReminderService = Depends(get_agent_reminder_service),
) -> AgentReminder:
    return await agent_reminder_service.update_agent_reminder(
        user_id=user_id,
        reminder_id=reminder_id,
        reminder_description=reminder_description,
        due_date=due_date,
    )


@mcp_app.tool(
    name="deleteAgentReminder",
    description="Delete a reminder for the user.",
)
async def delete_agent_reminder(
    user_id: Annotated[str, "The id of the user the reminder belongs to"],
    reminder_id: Annotated[str, "The unique id of the reminder to delete"],
    agent_reminder_service: AgentReminderService = Depends(get_agent_reminder_service),
) -> None:
    await agent_reminder_service.delete_agent_reminder(
        user_id=user_id,
        reminder_id=reminder_id,
    )


@mcp_app.prompt
def get_invstment_advisor_prompt(user_id: str) -> str:
    return INVESTMENT_ADVISOR_PROMPT.format(user_id=user_id)

if __name__ == "__main__":
    mcp_app.run(transport="http", port=9000)