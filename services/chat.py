from abc import ABC, abstractmethod
import datetime as dt
import json

from errors.session import SessionNotFoundError
from models.session import (
    Message,
    MessageRole,
)
from services.session import (
    SessionService,
)
from services.agent import (
    AgentService,
    TextResponseFormat,
)
from models.gen_ui_models import GenerativeUIResponse


class ChatService(ABC):
    @abstractmethod
    async def generate_text_response(self, session_id: str, message: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def generate_gen_ui_response(self, session_id: str, message: str) -> GenerativeUIResponse:
        raise NotImplementedError


class AgenticChatService(ChatService):
    def __init__(self, session_service: SessionService, agent_service: AgentService):
        self._agent_service = agent_service
        self._session_service = session_service
    
    async def generate_text_response(self, session_id: str, message: str) -> str:
        # Get the session
        session = await self._session_service.get_session(session_id)
        if not session:
            raise SessionNotFoundError(f"Session {session_id} not found")
        
        conversation = session.messages
        user_id = session.user_id
        conversation.append(Message(role=MessageRole.USER, content=message))

        response_model = await self._agent_service.generate_response(user_id, conversation, TextResponseFormat)
        agent_response = response_model.response

        # Store the message and response in the session
        await self._session_service.add_message(
            session_id,
            Message(
                role=MessageRole.USER,
                content=message,
                created_at=dt.datetime.now(dt.timezone.utc).isoformat(),
            ),
        )
        await self._session_service.add_message(
            session_id,
            Message(
                role=MessageRole.AGENT,
                content=agent_response,
                created_at=dt.datetime.now(dt.timezone.utc).isoformat(),
            ),
        )
        # Return the response
        return agent_response

    async def generate_gen_ui_response(self, session_id: str, message: str) -> GenerativeUIResponse:
        # Get the session
        session = await self._session_service.get_session(session_id)
        if not session:
            raise SessionNotFoundError(f"Session {session_id} not found")
        
        conversation = session.messages
        user_id = session.user_id
        conversation.append(Message(role=MessageRole.USER, content=message))

        response_model = await self._agent_service.generate_response(user_id, conversation, GenerativeUIResponse)
        
        # Serialize the response components to a string for history storage
        # This keeps the context for future turns
        response_content_str = json.dumps([c.model_dump() for c in response_model.components])

        # Store the message and response in the session
        await self._session_service.add_message(
            session_id,
            Message(
                role=MessageRole.USER,
                content=message,
                created_at=dt.datetime.now(dt.timezone.utc).isoformat(),
            ),
        )
        await self._session_service.add_message(
            session_id,
            Message(
                role=MessageRole.AGENT,
                content=response_content_str,
                created_at=dt.datetime.now(dt.timezone.utc).isoformat(),
            ),
        )
        # Return the structured response
        return response_model
