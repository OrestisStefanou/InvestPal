from enum import Enum

from pydantic import BaseModel

class MessageRole(str, Enum):
    USER = "user"
    AGENT = "agent"


class Message(BaseModel):
    role: MessageRole
    content: str
    created_at: str | None = None


class Session(BaseModel):
    session_id: str
    user_id: str
    messages: list[Message]
