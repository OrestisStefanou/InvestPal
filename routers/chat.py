import http
from typing import (
    Any,
    Dict,
    Optional,
)

from fastapi import (
    APIRouter, 
    Depends,
    HTTPException,
)
from pydantic import (
    BaseModel,
    Field,
)

from errors.session import SessionNotFoundError
from services.chat import ChatService
from dependencies import get_chat_service

router = APIRouter()


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
):
    try:
        response = await chat_service.generate_response(
            request.session_id,
            request.message,
        )
    except SessionNotFoundError:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Session not found")

    return ChatResponse(response=response)
