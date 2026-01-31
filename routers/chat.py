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
from models.gen_ui_models import GenerativeUIResponseFormat

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
        response = await chat_service.generate_text_response(
            request.session_id,
            request.message,
        )
    except SessionNotFoundError:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Session not found")

    return ChatResponse(response=response)


class GenUIRequest(BaseModel):
    session_id: str
    message: str


class GenUIResponse(GenerativeUIResponseFormat):
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Response-level metadata"
    )


@router.post("/chat/gen-ui", response_model=GenerativeUIResponseFormat)
async def chat_gen_ui(
    request: GenUIRequest,
    chat_service: ChatService = Depends(get_chat_service),
):
    try:
        response = await chat_service.generate_gen_ui_response(
            request.session_id,
            request.message,
        )
    except SessionNotFoundError:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Session not found")

    return GenUIResponse(
        components=response.components,
        metadata={},
    )
