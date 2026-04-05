from pydantic import BaseModel, Field


class AgentReminder(BaseModel):
    user_id: str = Field(description="The user_id for which the reminder was created")
    reminder_id: str = Field(description="Unique id of the reminder")
    reminder_description: str = Field(description="The description of the reminder")
    created_at: str = Field(description="The date-time of creation of the reminder in ISO format")
    due_date: str | None = Field(default=None, description="The due date of the reminder in YYYY-MM-DD format")
