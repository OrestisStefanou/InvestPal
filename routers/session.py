from enum import Enum
import http

from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException,
)
from pydantic import BaseModel
from pymongo import AsyncMongoClient

from services.session import (
    MongoDBSessionService, 
    SessionAlreadyExistsError,
)
from services.user_context import  UserContextNotFoundError
from dependencies import get_db_client

router = APIRouter()

class CreateSessionRequest(BaseModel):
    """
    Request model for creating a new session.
    
    Attributes:
        user_id (str): The ID of the user.
        session_id (str | None): The ID of the session. If not provided, a new ID will be generated.
    """
    user_id: str
    session_id: str | None = None


class RoleSchema(str, Enum):
    USER = "user"
    AGENT = "agent"


class MessageSchema(BaseModel):
    role: RoleSchema
    content: str


class SessionSchema(BaseModel):
    session_id: str
    user_id: str
    messages: list[MessageSchema]


@router.post("/session", response_model=SessionSchema, status_code=http.HTTPStatus.CREATED)
async def create_session(request: CreateSessionRequest, db_client: AsyncMongoClient = Depends(get_db_client)):
    session_service = MongoDBSessionService(
        mongo_client=db_client,
    )
    try:
        session = await session_service.create_session(request.user_id, request.session_id)
    except SessionAlreadyExistsError as e:
        raise HTTPException(status_code=http.HTTPStatus.CONFLICT, detail=str(e))
    except UserContextNotFoundError as e:
        raise HTTPException(status_code=http.HTTPStatus.BAD_REQUEST, detail=str(e))
    
    return SessionSchema(
        session_id=session.sessionID,
        user_id=session.user_id,
        messages=[],
    )


@router.get("/session/{session_id}", response_model=SessionSchema)
async def get_session(session_id: str, db_client: AsyncMongoClient = Depends(get_db_client)):
    session_service = MongoDBSessionService(
        mongo_client=db_client,
    )
    session = await session_service.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Session not found")
    
    # Convert Message objects to MessageSchema objects
    messages = [MessageSchema(role=RoleSchema(message.role), content=message.content) for message in session.messages]

    return SessionSchema(
        session_id=session.sessionID,
        user_id=session.user_id,
        messages=messages,
    )
