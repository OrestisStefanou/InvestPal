from abc import ABC, abstractmethod
import datetime as dt

from pydantic import BaseModel
from pymongo import (
    AsyncMongoClient,
    ReturnDocument,
)

from config import settings
class UserContextAlreadyExistsError(Exception):
    pass


class UserContextNotFoundError(Exception):
    pass
from models.user_context import (
    UserContext,
)


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
