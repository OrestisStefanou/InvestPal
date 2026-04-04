from pydantic import BaseModel, Field


class UserContext(BaseModel):
    user_id: str = Field(description="The unique identifier for the user")
    user_profile: dict = Field(description="A dictionary containing user preferences and profile information")
    created_at: str | None = Field(default=None, description="The ISO timestamp when the context was created")
    updated_at: str | None = Field(default=None, description="The ISO timestamp when the context was last updated")


class UserConversationNotes(BaseModel):
    user_id: str = Field(description="The unique identifier for the user")
    date: str = Field(description="The date in YYYY-MM-DD format")
    notes: dict = Field(description="A key-value store containing short, concise notes about the conversation on this date")