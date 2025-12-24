from abc import ABC, abstractmethod
from enum import Enum
import uuid

from pydantic import BaseModel
from pymongo import AsyncMongoClient

class MessageRole(str, Enum):
    USER = "user"
    AGENT = "agent"


class Message(BaseModel):
    role: MessageRole
    content: str


class Session(BaseModel):
    sessionID: str
    user_id: str
    messages: list[Message]


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


class SessionNotFoundError(Exception):
    pass


class SessionAlreadyExistsError(Exception):
    pass


class MongoDBSessionService(SessionService):
    def __init__(self, mongo_client: AsyncMongoClient, db_name: str, collection_name: str):
        self.db = mongo_client[db_name]
        self.collection = self.db[collection_name]

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
        session_id = session_id or str(uuid.uuid4())
        # Check if session already exists
        session = await self.get_session(session_id)
        if session:
            raise SessionAlreadyExistsError(f"Session {session_id} already exists")
    
        session = Session(sessionID=session_id, user_id=user_id, messages=[])
        await self.collection.insert_one(session.model_dump())
        return session
    
    async def get_session(self, session_id: str) -> Session | None:
        doc = await self.collection.find_one({"sessionID": session_id})
        if doc:
            return Session(**doc)

        return None

    async def add_message(self, session_id: str, message: Message) -> Session | None:
        session = await self.get_session(session_id)
        if not session:
            raise SessionNotFoundError("Session not found")

        session.messages.append(message)
        await self.collection.update_one({"sessionID": session_id}, {"$set": session.model_dump()})
        return session