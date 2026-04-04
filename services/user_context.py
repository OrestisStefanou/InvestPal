from abc import ABC, abstractmethod
import datetime as dt
from typing import Any

from pydantic import BaseModel
from pymongo import (
    AsyncMongoClient,
    ReturnDocument,
)

from config import settings
from models.user_context import (
    UserContext,
    UserConversationNotes,
)


class UserContextAlreadyExistsError(Exception):
    pass


class UserContextNotFoundError(Exception):
    pass


class UserContextService(ABC):
    @abstractmethod
    async def create_user_context(
        self, 
        user_id: str,
        user_profile: dict | None = None,
    ) -> UserContext | None:
        pass

    @abstractmethod
    async def get_user_context(self, user_id: str) -> UserContext | None:
        pass

    @abstractmethod
    async def update_user_context(
        self,
        user_id: str,
        user_profile: dict | None = None,
    ) -> UserContext:
        pass

    @abstractmethod
    async def get_user_conversation_notes(
        self,
        user_id: str,
        date: str | None = None,
    ) -> list[UserConversationNotes]:
        pass

    @abstractmethod
    async def update_user_conversation_notes(
        self,
        user_id: str,
        date: str,
        notes: dict[str, Any],
    ) -> None:
        pass


class UserContextMongoDoc(BaseModel):
    user_id: str
    user_profile: dict
    created_at: str | None = None
    updated_at: str | None = None


class UserConversationNotesMongoDoc(BaseModel):
    user_id: str
    date: str
    notes: dict


class MongoDBUserContextService(UserContextService):
    def __init__(self, mongo_client: AsyncMongoClient):
        self.db = mongo_client[settings.MONGO_DB_NAME]

    async def create_user_context(
        self, 
        user_id: str,
        user_profile: dict | None = None,
    ) -> UserContext | None:
        """
        Create a new user context for the given user_id.

        Args:
            user_id: The user_id for which to create the user context.
            user_profile: The user profile to be stored in the user context.
        
        Raises:
            UserContextAlreadyExistsError: If a user context for the given user_id already exists.

        Returns:
            The created user context.
        """
        user_context_collection = self.db[settings.USER_CONTEXT_COLLECTION_NAME]
        # Check if user context for user_id already exists
        existing_user_context = await user_context_collection.find_one({"user_id": user_id})
        if existing_user_context:
            raise UserContextAlreadyExistsError(f"User context already exists for user_id: {user_id}")

        user_context = UserContextMongoDoc(
            user_id=user_id,
            user_profile=user_profile if user_profile is not None else {},
            created_at=dt.datetime.now(dt.timezone.utc).isoformat(),
        )
        await user_context_collection.insert_one(user_context.model_dump())

        return UserContext(
            user_id=user_id,
            user_profile=user_profile if user_profile is not None else {},
            created_at=dt.datetime.now(dt.timezone.utc).isoformat(),
        )

    async def get_user_context(self, user_id: str) -> UserContext | None:
        """
        Get the user context for the given user_id.

        Args:
            user_id: The user_id for which to get the user context.
        
        Returns:
            The user context for the given user_id. None if no user context exists for the given user_id.
        """
        user_context_collection = self.db[settings.USER_CONTEXT_COLLECTION_NAME]
        user_context_doc = await user_context_collection.find_one({"user_id": user_id})
        if not user_context_doc:
            return None

        mongo_doc = UserContextMongoDoc.model_validate(user_context_doc)

        return UserContext(
            user_id=mongo_doc.user_id,
            user_profile=mongo_doc.user_profile,
            created_at=mongo_doc.created_at,
            updated_at=mongo_doc.updated_at,
        )

    async def update_user_context(
        self, 
        user_id: str,
        user_profile: dict | None = None,
    ) -> UserContext:
        """
        Update the user context for the given user_id.

        Args:
            user_id: The user_id for which to update the user context.
            user_profile: The user profile to be updated.

        Raises:
            UserContextNotFoundError: If no user context exists for the given user_id.

        Returns:
            The updated user context.
        """
        user_context_collection = self.db[settings.USER_CONTEXT_COLLECTION_NAME]

        now = dt.datetime.now(dt.timezone.utc).isoformat()

        update_data = {"updated_at": now}
        if user_profile is not None:
            update_data["user_profile"] = user_profile

        updated_doc = await user_context_collection.find_one_and_update(
            {"user_id": user_id},
            {
                "$set": update_data
            },
            return_document=ReturnDocument.AFTER,
        )

        if not updated_doc:
            raise UserContextNotFoundError(
                f"User context not found for user_id: {user_id}"
            )

        mongo_result = UserContextMongoDoc.model_validate(updated_doc)

        return UserContext(
            user_id=mongo_result.user_id,
            user_profile=mongo_result.user_profile,
            created_at=mongo_result.created_at,
            updated_at=mongo_result.updated_at,
        )

    async def get_user_conversation_notes(
        self,
        user_id: str,
        date: str | None = None,
    ) -> list[UserConversationNotes]:
        """
        Get conversation notes for the given user_id, optionally filtered by date.

        Args:
            user_id: The user_id for which to get conversation notes.
            date: Optional date string in YYYY-MM-DD format to filter notes by a specific date.

        Returns:
            A list of UserConversationNotes models.
        """
        collection = self.db[settings.USER_CONVERSATION_NOTES_COLLECTION_NAME]
        query: dict[str, Any] = {"user_id": user_id}
        if date:
            query["date"] = date

        cursor = collection.find(query)
        docs = await cursor.to_list(length=None)

        return [
            UserConversationNotes(
                user_id=doc["user_id"],
                date=doc["date"],
                notes=doc["notes"],
            )
            for doc in docs
        ]

    async def update_user_conversation_notes(
        self,
        user_id: str,
        date: str,
        notes: dict[str, Any],
    ) -> None:
        """
        Create or update the conversation notes for the given user_id and date.
        The provided notes are merged with any existing ones for that date using 
        dot notation (only keys provided will be overwritten or added).

        Args:
            user_id: The user_id for which to update conversation notes.
            date: The date string in YYYY-MM-DD format.
            notes: A dict containing the notes to store or merge for this date.
        """
        collection = self.db[settings.USER_CONVERSATION_NOTES_COLLECTION_NAME]
        
        if not notes:
            # If notes is empty, just ensure the document exists with an empty notes object if new
            await collection.update_one(
                {"user_id": user_id, "date": date},
                {"$setOnInsert": {"notes": {}}},
                upsert=True,
            )
            return

        # Use dot notation to update specific keys within the notes object without overwriting others
        update_data = {f"notes.{k}": v for k, v in notes.items()}
        await collection.update_one(
            {"user_id": user_id, "date": date},
            {"$set": update_data},
            upsert=True,
        )
