import asyncio
import uuid
from abc import ABC, abstractmethod

from models.session import (
    Message,
    MessageRole,
    Session,
)
from repos.sessions import SessionsTable


class SessionNotFoundError(Exception):
    pass


class SessionAlreadyExistsError(Exception):
    pass


class SessionService(ABC):
    @abstractmethod
    async def create_session(self, session_id: str | None = None, name: str | None = None) -> Session:
        pass

    @abstractmethod
    async def get_session(self, session_id: str) -> Session | None:
        pass

    @abstractmethod
    async def add_message(self, session_id: str, message: Message) -> Session | None:
        pass

    @abstractmethod
    async def get_sessions(self) -> list[Session]:
        pass


class TursoSessionService(SessionService):
    def __init__(self, table: SessionsTable):
        self._table = table

    async def create_session(self, session_id: str | None = None, name: str | None = None) -> Session:
        """
        Create a new session.

        Args:
            session_id: The ID of the session. If not provided, a new ID will be generated.
            name: The name of the session. Defaults to the session id.

        Returns:
            Session: The created session.

        Raises:
            SessionAlreadyExistsError: If the session already exists.
        """
        if session_id:
            existing = await asyncio.to_thread(self._table.get_session, session_id)
            if existing:
                raise SessionAlreadyExistsError(f"Session {session_id} already exists")
        else:
            session_id = str(uuid.uuid4())

        row = await asyncio.to_thread(
            self._table.create_session, session_id, name or session_id
        )
        return Session(
            session_id=row.id,
            messages=[],
            name=row.name,
            created_at=row.created_at,
        )

    async def get_session(self, session_id: str) -> Session | None:
        row = await asyncio.to_thread(self._table.get_session, session_id)
        if not row:
            return None

        messages = await asyncio.to_thread(self._table.get_messages, session_id)
        return Session(
            session_id=row.id,
            messages=[
                Message(
                    role=MessageRole(message.role),
                    content=message.content,
                    created_at=message.created_at,
                )
                for message in messages
            ],
            name=row.name,
            created_at=row.created_at,
        )

    async def add_message(self, session_id: str, message: Message) -> Session | None:
        session = await self.get_session(session_id)
        if not session:
            raise SessionNotFoundError("Session not found")

        await asyncio.to_thread(
            self._table.add_message,
            session_id=session_id,
            role=MessageRole(message.role).value,
            content=message.content,
            created_at=message.created_at,
        )

        session.messages.append(message)
        return session

    async def get_sessions(self) -> list[Session]:
        """Session summaries, most recent first. Messages are not loaded."""
        rows = await asyncio.to_thread(self._table.get_sessions)
        return [
            Session(
                session_id=row.id,
                messages=[],
                name=row.name,
                created_at=row.created_at,
            )
            for row in rows
        ]
