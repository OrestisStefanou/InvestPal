from abc import ABC, abstractmethod
import uuid

from pydantic import BaseModel
from pymongo import AsyncMongoClient

from config import settings
from models.session import (
    Session,
    Message,
)
from errors.user_context import UserContextNotFoundError
from errors.session import (
    SessionAlreadyExistsError,
    SessionNotFoundError,
)


class SessionService(ABC):
    @abstractmethod
    async def create_session(self, user_id: str, session_id: str | None = None) -> Session:
        pass

    @abstractmethod
    async def get_session(self, session_id: str) -> Session | None:
        pass

    @abstractmethod
    async def add_message(self, session_id: str, message: Message) -> Session | None:
        pass


class MessageMongoDoc(Message):
    pass


class SessionMongoDoc(BaseModel):
    sessionID: str
    user_id: str
    messages: list[MessageMongoDoc]


class MongoDBSessionService(SessionService):
    def __init__(self, mongo_client: AsyncMongoClient):
        self.db = mongo_client[settings.MONGO_DB_NAME]

    async def create_session(self, user_id: str, session_id: str | None = None) -> Session:
        """
        Create a new session for the user.
        
        Args:
            user_id (str): The ID of the user.
            session_id (str | None): The ID of the session. If not provided, a new ID will be generated.
        
        Returns:
            Session: The created session.
        
        Raises:
            SessionAlreadyExistsError: If the session already exists.
        """
        session_collection = self.db[settings.SESSION_COLLECTION_NAME]
        user_context_collection = self.db[settings.USER_CONTEXT_COLLECTION_NAME]

        if session_id:
            # Check if session already exists for the given id
            session = await self.get_session(session_id)
            if session:
                raise SessionAlreadyExistsError(f"Session {session_id} already exists")
        else:
            session_id = str(uuid.uuid4())

        # Check if user_id is valid
        user_context = await user_context_collection.find_one({"userid": user_id})
        if not user_context:
            raise UserContextNotFoundError(f"User context not found for user_id: {user_id}")

        session_doc = SessionMongoDoc(sessionID=session_id, user_id=user_id, messages=[])
        await session_collection.insert_one(session_doc.model_dump())

        return Session(
            session_id=session_doc.sessionID,
            user_id=session_doc.user_id,
            messages=[],
        )
    
    async def get_session(self, session_id: str) -> Session | None:
        session_collection = self.db[settings.SESSION_COLLECTION_NAME]
        doc = await session_collection.find_one({"sessionID": session_id})
        if not doc:
            return None

        mongo_doc = SessionMongoDoc.model_validate(doc)

        return Session(
            session_id=mongo_doc.sessionID,
            user_id=mongo_doc.user_id,
            messages=[
                Message(
                    role=msg.role,
                    content=msg.content,
                    created_at=msg.created_at,
                )
                for msg in mongo_doc.messages
            ],
        )

    async def add_message(self, session_id: str, message: Message) -> Session | None:
        session_collection = self.db[settings.SESSION_COLLECTION_NAME]

        session = await self.get_session(session_id)
        if not session:
            raise SessionNotFoundError("Session not found")

        # Map Message to MessageMongoDoc
        message_doc = MessageMongoDoc(
            role=message.role,
            content=message.content,
            created_at=message.created_at,
        )

        await session_collection.update_one(
            {"sessionID": session_id},
            {"$push": {"messages": message_doc.model_dump()}}
        )

        session.messages.append(message)

        return session