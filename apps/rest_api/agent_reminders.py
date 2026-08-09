import http

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from pydantic import BaseModel

from services.agent_reminder import AgentReminderService
from dependencies import get_agent_reminder_service


router = APIRouter(tags=["Agent Reminders"])


class AgentReminderSchema(BaseModel):
    id: str
    description: str
    created_at: str
    due_date: str | None = None


@router.get("/agent_reminders", response_model=list[AgentReminderSchema])
async def get_agent_reminders(agent_reminder_service: AgentReminderService = Depends(get_agent_reminder_service)):
    reminders = await agent_reminder_service.get_agent_reminders()

    return [
        AgentReminderSchema(
            id=reminder.id,
            description=reminder.description,
            created_at=reminder.created_at,
            due_date=reminder.due_date,
        )
        for reminder in reminders
    ]
