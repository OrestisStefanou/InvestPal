import http

from fastapi import (
    APIRouter, 
    Depends,
    HTTPException,
)
from pydantic import BaseModel
from pymongo import AsyncMongoClient
from langchain_mcp_adapters.client import MultiServerMCPClient

from errors.session import SessionNotFoundError
from services.session import (
    MongoDBSessionService,
)
from services.chat import AgenticChatService
from services.agent import (
    AgentServiceWithMCP,
)
from dependencies import (
    get_db_client,
    get_mcp_client,
)
from models.gen_ui_models import GenerativeUIResponse

router = APIRouter()


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db_client: AsyncMongoClient = Depends(get_db_client), 
    mcp_client: MultiServerMCPClient = Depends(get_mcp_client),
):
    session_service = MongoDBSessionService(
        mongo_client=db_client,
    )
    agent_service = AgentServiceWithMCP(
        mcp_client=mcp_client,
    )
    chat_service = AgenticChatService(session_service, agent_service)
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


@router.post("/chat/gen-ui", response_model=GenerativeUIResponse)
async def chat_gen_ui(
    request: GenUIRequest,
    db_client: AsyncMongoClient = Depends(get_db_client), 
    mcp_client: MultiServerMCPClient = Depends(get_mcp_client),
):
    session_service = MongoDBSessionService(
        mongo_client=db_client,
    )
    agent_service = AgentServiceWithMCP(
        mcp_client=mcp_client,
    )
    chat_service = AgenticChatService(session_service, agent_service)
    try:
        response = await chat_service.generate_gen_ui_response(
            request.session_id,
            request.message,
        )
    except SessionNotFoundError:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Session not found")

    return response
