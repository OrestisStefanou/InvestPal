from enum import Enum
import http

from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException,
)
from pydantic import BaseModel

from services.session import (
    SessionService, 
)
from services.session import SessionAlreadyExistsError
from services.user_context import  UserContextNotFoundError
from dependencies import get_session_service


router = APIRouter()


class CreateSessionRequest(BaseModel):
    """
    Request model for creating a new session.
    
    Attributes:
        user_id (str): The ID of the user.
        session_id (str | None): The ID of the session. If not provided, a new ID will be generated.
        name (str | None): The name of the session. If not provided, the session_id will be used as the name.
    """
    user_id: str
    session_id: str | None = None
    name: str | None = None


class RoleSchema(str, Enum):
    USER = "user"
    AGENT = "agent"


class MessageSchema(BaseModel):
    role: RoleSchema
    content: str
    created_at: str | None


class SessionSchema(BaseModel):
    session_id: str
    user_id: str
    messages: list[MessageSchema]
    name: str
    created_at: str


class SessionSummarySchema(BaseModel):
    session_id: str
    user_id: str
    name: str
    created_at: str


@router.post("/session", response_model=SessionSchema, status_code=http.HTTPStatus.CREATED)
async def create_session(request: CreateSessionRequest, session_service: SessionService = Depends(get_session_service)):
    try:
        session = await session_service.create_session(request.user_id, request.session_id, request.name)
    except SessionAlreadyExistsError as e:
        raise HTTPException(status_code=http.HTTPStatus.CONFLICT, detail=str(e))
    except UserContextNotFoundError as e:
        raise HTTPException(status_code=http.HTTPStatus.BAD_REQUEST, detail=str(e))
    
    return SessionSchema(
        session_id=session.session_id,
        user_id=session.user_id,
        messages=[],
        name=session.name,
        created_at=session.created_at,
    )


@router.get("/session/{session_id}", response_model=SessionSchema)
async def get_session(session_id: str, session_service: SessionService = Depends(get_session_service)):
    session = await session_service.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Session not found")
    
    # Convert Message objects to MessageSchema objects
    messages = [
        MessageSchema(
            role=RoleSchema(message.role),
            content=message.content,
            created_at=message.created_at,
        )
        for message in session.messages
    ]

    return SessionSchema(
        session_id=session.session_id,
        user_id=session.user_id,
        messages=messages,
        name=session.name,
        created_at=session.created_at,
    )


@router.get("/sessions/{user_id}", response_model=list[SessionSummarySchema])
async def list_user_sessions(user_id: str, session_service: SessionService = Depends(get_session_service)):
    sessions = await session_service.get_user_sessions(user_id)
    
    return [
        SessionSummarySchema(
            session_id=session.session_id,
            user_id=session.user_id,
            name=session.name,
            created_at=session.created_at,
        )
        for session in sessions
    ]
