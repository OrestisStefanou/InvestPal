from pydantic import BaseModel, Field


class AgentReminder(BaseModel):
    id: str = Field(description="Unique id of the reminder")
    description: str = Field(description="The description of the reminder")
    created_at: str = Field(description="The date-time of creation of the reminder in ISO format")
    due_date: str | None = Field(default=None, description="The due date of the reminder in YYYY-MM-DD format")
