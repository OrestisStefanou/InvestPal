from dataclasses import dataclass
import datetime as dt


from pydantic import (
    BaseModel,
    Field,
)
from langchain.tools import (
    tool,
    ToolRuntime,
)
from langchain_mcp_adapters.client import MultiServerMCPClient

from models.user_context import (
    UserContext,
    UserConversationNotes,
)
from models.agent_reminder import AgentReminder
from services.user_context import UserContextService
from services.agent_reminder import AgentReminderService


@dataclass
class UserContextToolsRuntimeContext:
    user_context_service: UserContextService


@dataclass
class AgentReminderToolsRuntimeContext:
    agent_reminder_service: AgentReminderService


class UpdateUserContextToolInput(BaseModel):
    user_id: str = Field(description="The id of the user to update the context for")
    user_profile: dict = Field(description="General information about the user. Must provide the complete user profile as it will replace the existing one.")


@tool(
    "updateUserContext",
    args_schema=UpdateUserContextToolInput,
    description="Update the user context(for the given user_id) including user profile. Note: The provided context will completely replace the existing one, so the entire updated object must be provided.",
)
async def update_user_context(
    runtime: ToolRuntime[UserContextToolsRuntimeContext],
    user_id: str,
    user_profile: dict,
) -> UserContext:
    user_context_service = runtime.context.user_context_service
    updated_user_context = await user_context_service.update_user_context(
        user_id=user_id,
        user_profile=user_profile,
    )

    return updated_user_context


@tool("getUserContext")
async def get_user_context(runtime: ToolRuntime[UserContextToolsRuntimeContext], user_id: str) -> UserContext:
    """Get the user context including user profile and portfolio holdings.

    Args:
        user_id: The id of the user to get the context for
    """
    user_context_service = runtime.context.user_context_service
    user_context = await user_context_service.get_user_context(user_id)
    return user_context


@tool("getCurrentDatetime")
async def get_current_datetime() -> str:
    """
    Get the current datetime.
    """
    return dt.datetime.now().isoformat()


class GetUserConversationNotesToolInput(BaseModel):
    user_id: str = Field(description="The id of the user to get conversation notes for")
    limit: int | None = Field(
        default=5,
        description="Maximum number of dates to return, ordered by most recent first. Defaults to 5. Pass None to return all notes.",
    )


@tool(
    "getUserConversationNotes",
    args_schema=GetUserConversationNotesToolInput,
    description=(
        "Retrieve conversation notes for a user, ordered by most recent date first. "
        "Allows recalling specific details from past conversations."
    ),
)
async def get_user_conversation_notes(
    runtime: ToolRuntime[UserContextToolsRuntimeContext],
    user_id: str,
    limit: int | None = 5,
) -> list[UserConversationNotes]:
    user_context_service = runtime.context.user_context_service
    return await user_context_service.get_user_conversation_notes(user_id=user_id, limit=limit)


class UpdateUserConversationNotesToolInput(BaseModel):
    user_id: str = Field(description="The id of the user to update conversation notes for")
    date: str = Field(description="The date of the conversation in YYYY-MM-DD format")
    notes: dict = Field(
        description=(
            "A key-value store of short, concise notes about the conversation on this date. "
            "Notes will be MERGED into existing ones for this date (only keys provided will "
            "be overwritten or added). Keep notes brief and focused on information useful "
            "for future investment advice."
        )
    )


@tool(
    "updateUserConversationNotes",
    args_schema=UpdateUserConversationNotesToolInput,
    description=(
        "Store or update conversation notes for a specific user and date. "
        "Use this to capture conversation-specific context such as topics discussed, "
        "questions asked, or recommendations given — information that is relevant to a particular "
        "conversation but not a permanent part of the user's profile. "
        "Updates are additive: any keys provided will overwrite or be added to existing notes for that date."
    ),
)
async def update_user_conversation_notes(
    runtime: ToolRuntime[UserContextToolsRuntimeContext],
    user_id: str,
    date: str,
    notes: dict,
) -> None:
    user_context_service = runtime.context.user_context_service
    await user_context_service.update_user_conversation_notes(
        user_id=user_id,
        date=date,
        notes=notes,
    )


class CreateAgentReminderToolInput(BaseModel):
    user_id: str = Field(description="The id of the user to create the reminder for")
    reminder_description: str = Field(description="The description of the reminder")
    due_date: str | None = Field(
        default=None,
        description="Optional due date for the reminder in YYYY-MM-DD format",
    )


@tool(
    "createAgentReminder",
    args_schema=CreateAgentReminderToolInput,
    description="Create a new reminder for the user.",
)
async def create_agent_reminder(
    runtime: ToolRuntime[AgentReminderToolsRuntimeContext],
    user_id: str,
    reminder_description: str,
    due_date: str | None = None,
) -> AgentReminder:
    agent_reminder_service = runtime.context.agent_reminder_service
    return await agent_reminder_service.create_agent_reminder(
        user_id=user_id,
        reminder_description=reminder_description,
        due_date=due_date,
    )


@tool("getAgentReminders")
async def get_agent_reminders(
    runtime: ToolRuntime[AgentReminderToolsRuntimeContext],
    user_id: str,
) -> list[AgentReminder]:
    """Get all reminders for the given user.

    Args:
        user_id: The id of the user to get reminders for
    """
    agent_reminder_service = runtime.context.agent_reminder_service
    return await agent_reminder_service.get_agent_reminders(user_id=user_id)


class UpdateAgentReminderToolInput(BaseModel):
    user_id: str = Field(description="The id of the user the reminder belongs to")
    reminder_id: str = Field(description="The unique id of the reminder to update")
    reminder_description: str | None = Field(
        default=None,
        description="New description for the reminder. If omitted, the existing description is kept.",
    )
    due_date: str | None = Field(
        default=None,
        description="New due date for the reminder in YYYY-MM-DD format. If omitted, the existing due date is kept.",
    )


@tool(
    "updateAgentReminder",
    args_schema=UpdateAgentReminderToolInput,
    description="Update an existing reminder for the user.",
)
async def update_agent_reminder(
    runtime: ToolRuntime[AgentReminderToolsRuntimeContext],
    user_id: str,
    reminder_id: str,
    reminder_description: str | None = None,
    due_date: str | None = None,
) -> AgentReminder:
    agent_reminder_service = runtime.context.agent_reminder_service
    return await agent_reminder_service.update_agent_reminder(
        user_id=user_id,
        reminder_id=reminder_id,
        reminder_description=reminder_description,
        due_date=due_date,
    )


class DeleteAgentReminderToolInput(BaseModel):
    user_id: str = Field(description="The id of the user the reminder belongs to")
    reminder_id: str = Field(description="The unique id of the reminder to delete")


@tool(
    "deleteAgentReminder",
    args_schema=DeleteAgentReminderToolInput,
    description="Delete a reminder for the user.",
)
async def delete_agent_reminder(
    runtime: ToolRuntime[AgentReminderToolsRuntimeContext],
    user_id: str,
    reminder_id: str,
) -> None:
    agent_reminder_service = runtime.context.agent_reminder_service
    await agent_reminder_service.delete_agent_reminder(
        user_id=user_id,
        reminder_id=reminder_id,
    )
