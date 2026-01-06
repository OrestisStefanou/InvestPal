from abc import ABC, abstractmethod
import datetime as dt

from pydantic import BaseModel
from pymongo import (
    AsyncMongoClient,
    ReturnDocument,
)

from config import settings

# The naming of the fields is done to match mcp server schema
class UserPortfolioHolding(BaseModel):
    assetclass: str
    symbol: str
    name: str
    quantity: float

class UserContext(BaseModel):
    userid: str
    userprofile: dict
    userportfolio: list[UserPortfolioHolding]
    createdat: str | None = None
    updatedat: str | None = None


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
        user_portfolio: list[UserPortfolioHolding] | None = None,
    ) -> UserContext | None:
        pass

    @abstractmethod
    async def get_user_context(self, user_id: str) -> UserContext | None:
        pass

    @abstractmethod
    async def update_user_context(self, user_id: str, user_context: UserContext) -> UserContext | None:
        pass

class MongoDBUserContextService(UserContextService):
    def __init__(self, mongo_client: AsyncMongoClient):
        self.db = mongo_client[settings.MONGO_DB_NAME]

    async def create_user_context(
        self, 
        user_id: str,
        user_profile: dict | None = None,
        user_portfolio: list[UserPortfolioHolding] | None = None,
    ) -> UserContext | None:
        """
        Create a new user context for the given user_id.

        Args:
            user_id: The user_id for which to create the user context.
            user_profile: The user profile to be stored in the user context.
            user_portfolio: The user portfolio to be stored in the user context.
        
        Raises:
            UserContextAlreadyExistsError: If a user context for the given user_id already exists.

        Returns:
            The created user context.
        """
        user_context_collection = self.db[settings.USER_CONTEXT_COLLECTION_NAME]
        # Check if user context for user_id already exists
        existing_user_context = await user_context_collection.find_one({"userid": user_id})
        if existing_user_context:
            raise UserContextAlreadyExistsError(f"User context already exists for user_id: {user_id}")

        user_context = UserContext(
            userid=user_id,
            userprofile=user_profile if user_profile is not None else {},
            userportfolio=user_portfolio if user_portfolio is not None else [],
            createdat=dt.datetime.now(dt.timezone.utc).isoformat(),
        )
        await user_context_collection.insert_one(user_context.model_dump())
        return user_context

    async def get_user_context(self, user_id: str) -> UserContext | None:
        """
        Get the user context for the given user_id.

        Args:
            user_id: The user_id for which to get the user context.
        
        Returns:
            The user context for the given user_id. None if no user context exists for the given user_id.
        """
        user_context_collection = self.db[settings.USER_CONTEXT_COLLECTION_NAME]
        user_context = await user_context_collection.find_one({"userid": user_id})
        if not user_context:
            return None

        return UserContext(**user_context)

    async def update_user_context(self, user_id: str, user_context: UserContext) -> UserContext:
        """
        Update the user context for the given user_id.

        Args:
            user_id: The user_id for which to update the user context.
            user_context: The user context to be updated.

        Raises:
            UserContextNotFoundError: If no user context exists for the given user_id.

        Returns:
            The updated user context.
        """
        user_context_collection = self.db[settings.USER_CONTEXT_COLLECTION_NAME]

        now = dt.datetime.now(dt.timezone.utc).isoformat()

        update_data = user_context.model_dump(
            exclude={"createdat", "updatedat", "userid"}
        )

        updated_user_context = await user_context_collection.find_one_and_update(
            {"userid": user_id},
            {
                "$set": {
                    **update_data,
                    "updatedat": now,
                }
            },
            return_document=ReturnDocument.AFTER,
        )

        if not updated_user_context:
            raise UserContextNotFoundError(
                f"User context not found for user_id: {user_id}"
            )

        return UserContext(**updated_user_context)
