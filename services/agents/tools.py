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
