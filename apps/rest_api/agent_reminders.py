from fastapi import (
    APIRouter,
    Depends,
)
from pydantic import BaseModel

from services.agent_reminder import AgentReminderService
from dependencies import get_agent_reminder_service


router = APIRouter()


class AgentReminderSchema(BaseModel):
    user_id: str
    reminder_id: str
    reminder_description: str
    created_at: str
    due_date: str | None = None


@router.get("/agent_reminders/{user_id}", response_model=list[AgentReminderSchema])
async def get_agent_reminders(user_id: str, agent_reminder_service: AgentReminderService = Depends(get_agent_reminder_service)):
    reminders = await agent_reminder_service.get_agent_reminders(user_id)

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
