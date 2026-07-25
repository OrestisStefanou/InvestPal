import asyncio
from abc import ABC, abstractmethod
import datetime as dt

from pydantic import BaseModel
from pymongo import (
    AsyncMongoClient,
    ReturnDocument,
)

from config import settings
from models.user_context import (
    UserContext,
    UserConversationNote,
    UserProfileNote,
)
from repos.user_conversation_notes import UserConversationNotesTable
from repos.user_profile_notes import UserProfileNotesTable



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


class UserContextMongoDoc(BaseModel):
    user_id: str
    user_profile: dict
    created_at: str | None = None
    updated_at: str | None = None


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


class UserConversationNotesService:
    def __init__(self, table: UserConversationNotesTable):
        self.table = table

    async def get_user_conversation_notes(
        self,
        limit: int | None = None,
    ) -> list[UserConversationNote]:
        """
        Get conversation notes ordered by most recent first.

        Args:
            limit: Maximum number of notes to return. If None, returns all notes.

        Returns:
            A list of UserConversationNote models ordered by date descending.
        """
        rows = await asyncio.to_thread(self.table.get_notes, limit)
        return [
            UserConversationNote(
                id=row.id,
                date=row.date,
                note=row.note,
                created_at=row.created_at,
            )
            for row in rows
        ]

    async def create_user_conversation_note(
        self,
        note: str,
        date: str | None = None,
    ) -> UserConversationNote:
        """
        Create a conversation note for the given date. A date can hold any
        number of notes.

        Args:
            note: The note to store for this date.
            date: The date string in YYYY-MM-DD format. Defaults to today.

        Raises:
            ValueError: If date is provided and is not in YYYY-MM-DD format.

        Returns:
            The created note.
        """
        if date is None:
            date = dt.date.today().isoformat()
        else:
            try:
                dt.datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"Invalid date format: {date}. Expected YYYY-MM-DD.")

        row = await asyncio.to_thread(self.table.create_note, date, note)
        return UserConversationNote(
            id=row.id,
            date=row.date,
            note=row.note,
            created_at=row.created_at,
        )


class UserProfileService:
    def __init__(self, table: UserProfileNotesTable):
        self.table = table

    async def create_user_profile_note(self, note: str) -> UserProfileNote:
        row = await asyncio.to_thread(self.table.create_user_profile_note, note)
        return UserProfileNote(
            id=row.id,
            note=row.note,
            created_at=row.created_at
        )

    async def get_user_profile_notes(self) -> list[UserProfileNote]:
        rows = await asyncio.to_thread(self.table.get_user_profile_notes, False)
        return [
            UserProfileNote(
                id=row.id,
                note=row.note,
                created_at=row.created_at
            )
            for row in rows
        ]

    async def mark_note_as_outdated(self, note_id: str) -> None:
        await asyncio.to_thread(self.table.mark_as_outdated, note_id)

