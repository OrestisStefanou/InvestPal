from datetime import datetime
from pydantic import BaseModel, Field


class UserConversationNote(BaseModel):
    id: str = Field(description="The unique identifier for the note")
    date: str = Field(description="The date of the conversation in YYYY-MM-DD format")
    note: str = Field(description="A short, concise note about the conversation on this date")
    created_at: str = Field(description="The ISO timestamp when the note was created")


class UserConversationNoteSearchResult(UserConversationNote):
    similarity: float = Field(
        description=(
            "How closely the note matches the search query in meaning, from 0.0 "
            "(unrelated) to 1.0 (identical meaning). Notes on the same broad topic "
            "typically score between 0.6 and 0.9, so judge relevance by comparing "
            "the scores in the result set rather than against a fixed threshold."
        )
    )


class UserProfileNote(BaseModel):
    id: str = Field(description="The unique identifier for the user profile note")
    note: str = Field(description="The content of the note")
    created_at: datetime = Field(description="The datetime when the note was created")