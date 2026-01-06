from abc import ABC, abstractmethod
import datetime as dt

from services.session import (
    SessionService,
    SessionNotFoundError,
    MessageRole,
    Message,
)
from services.agent import (
    AgentService,
    TextResponseFormat,
)


class ChatService(ABC):
    @abstractmethod
    async def generate_text_response(self, session_id: str, message: str) -> str:
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

        agent_response = await self._agent_service.generate_response(user_id, conversation, TextResponseFormat)

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
