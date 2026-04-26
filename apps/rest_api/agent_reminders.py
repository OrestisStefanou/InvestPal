import http

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from pydantic import BaseModel

from services.agent_reminder import AgentReminderService
from services.user_context import UserContextNotFoundError
from dependencies import get_agent_reminder_service


router = APIRouter(tags=["Agent Reminders"])


class AgentReminderSchema(BaseModel):
    user_id: str
    reminder_id: str
    reminder_description: str
    created_at: str
    due_date: str | None = None


@router.get("/agent_reminders/{user_id}", response_model=list[AgentReminderSchema])
async def get_agent_reminders(user_id: str, agent_reminder_service: AgentReminderService = Depends(get_agent_reminder_service)):
    try:
        reminders = await agent_reminder_service.get_agent_reminders(user_id)
    except UserContextNotFoundError as e:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail=str(e))

    return [
        AgentReminderSchema(
            user_id=reminder.user_id,
            reminder_id=reminder.reminder_id,
            reminder_description=reminder.reminder_description,
            created_at=reminder.created_at,
            due_date=reminder.due_date,
        )
        for reminder in reminders
    ]
