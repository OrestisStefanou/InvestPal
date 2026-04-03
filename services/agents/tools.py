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
)
from services.user_context import UserContextService


@dataclass
class UserContextToolsRuntimeContext:
    user_context_service: UserContextService


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
    date: str | None = Field(
        default=None,
        description="Optional date filter in YYYY-MM-DD format. If provided, returns notes only for that specific date. If omitted, returns notes for all dates.",
    )


@tool(
    "getUserConversationNotes",
    args_schema=GetUserConversationNotesToolInput,
    description=(
        "Retrieve conversation notes for a user, optionally filtered by date. "
        "Each entry in the returned list maps a date (YYYY-MM-DD) to its notes dict. "
        "IMPORTANT: Always call this tool before calling updateUserConversationNotes to read "
        "existing notes and avoid storing duplicate or redundant information."
    ),
)
async def get_user_conversation_notes(
    runtime: ToolRuntime[UserContextToolsRuntimeContext],
    user_id: str,
    date: str | None = None,
) -> list[dict]:
    user_context_service = runtime.context.user_context_service
    return await user_context_service.get_user_conversation_notes(user_id=user_id, date=date)


class UpdateUserConversationNotesToolInput(BaseModel):
    user_id: str = Field(description="The id of the user to update conversation notes for")
    date: str = Field(description="The date of the conversation in YYYY-MM-DD format")
    notes: dict = Field(
        description=(
            "A key-value store of short, concise notes about the conversation on this date. "
            "Notes will completely replace any existing notes for this date, so include all relevant "
            "information (merge with existing notes retrieved via getUserConversationNotes). "
            "Keep notes brief and focused on information useful for future investment advice."
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
        "IMPORTANT: Always call getUserConversationNotes first to retrieve existing notes before "
        "calling this tool, so you can merge new information without losing previous notes. "
        "The provided notes will completely replace existing notes for that date."
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
