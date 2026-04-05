import datetime as dt
import uuid
from abc import ABC, abstractmethod

from pydantic import BaseModel
from pymongo import (
    AsyncMongoClient,
    ReturnDocument,
)

from config import settings
from models.agent_reminder import AgentReminder


class AgentReminderNotFoundError(Exception):
    pass


class AgentReminderService(ABC):
    @abstractmethod
    async def create_agent_reminder(
        self,
        user_id: str,
        reminder_description: str,
        due_date: str | None = None,
    ) -> AgentReminder:
        pass

    @abstractmethod
    async def get_agent_reminders(
        self,
        user_id: str,
    ) -> list[AgentReminder]:
        pass

    @abstractmethod
    async def delete_agent_reminder(
        self,
        user_id: str,
        reminder_id: str,
    ) -> None:
        pass

    @abstractmethod
    async def update_agent_reminder(
        self,
        user_id: str,
        reminder_id: str,
        reminder_description: str | None = None,
        due_date: str | None = None,
    ) -> AgentReminder:
        pass


class AgentReminderMongoDoc(BaseModel):
    user_id: str
    reminder_id: str
    reminder_description: str
    created_at: str     # date-time in ISO format
    due_date: str | None = None # date in YYYY-MM-DD format


class MongoDBAgentReminderService(AgentReminderService):
    def __init__(self, mongo_client: AsyncMongoClient):
        self.db = mongo_client[settings.MONGO_DB_NAME]

    async def create_agent_reminder(
        self,
        user_id: str,
        reminder_description: str,
        due_date: str | None = None,
    ) -> AgentReminder:
        """
        Create a new reminder for the given user.

        Args:
            user_id: The user_id for which to create the reminder.
            reminder_description: The description of the reminder.
            due_date: Optional due date in YYYY-MM-DD format.

        Returns:
            The created reminder.
        """
        collection = self.db[settings.AGENT_REMINDERS_COLLECTION_NAME]
        reminder_id = str(uuid.uuid4())
        created_at = dt.datetime.now(dt.timezone.utc).isoformat()

        doc = AgentReminderMongoDoc(
            user_id=user_id,
            reminder_id=reminder_id,
            reminder_description=reminder_description,
            created_at=created_at,
            due_date=due_date,
        )
        await collection.insert_one(doc.model_dump())

        return AgentReminder(
            user_id=user_id,
            reminder_id=reminder_id,
            reminder_description=reminder_description,
            created_at=created_at,
            due_date=due_date,
        )

    async def get_agent_reminders(
        self,
        user_id: str,
    ) -> list[AgentReminder]:
        """
        Get all reminders for the given user.

        Args:
            user_id: The user_id for which to get reminders.

        Returns:
            A list of reminders for the given user. Empty list if none exist.
        """
        collection = self.db[settings.AGENT_REMINDERS_COLLECTION_NAME]
        cursor = collection.find({"user_id": user_id})
        docs = await cursor.to_list(length=None)

        return [
            AgentReminder(
                user_id=doc["user_id"],
                reminder_id=doc["reminder_id"],
                reminder_description=doc["reminder_description"],
                created_at=doc["created_at"],
                due_date=doc.get("due_date"),
            )
            for doc in docs
        ]

    async def delete_agent_reminder(
        self,
        user_id: str,
        reminder_id: str,
    ) -> None:
        """
        Delete a reminder for the given user.

        Args:
            user_id: The user_id the reminder belongs to.
            reminder_id: The unique id of the reminder to delete.

        Raises:
            AgentReminderNotFoundError: If no reminder exists for the given user_id and reminder_id.
        """
        collection = self.db[settings.AGENT_REMINDERS_COLLECTION_NAME]
        result = await collection.delete_one({"user_id": user_id, "reminder_id": reminder_id})
        if result.deleted_count == 0:
            raise AgentReminderNotFoundError(f"Agent reminder not found for reminder_id: {reminder_id}")

    async def update_agent_reminder(
        self,
        user_id: str,
        reminder_id: str,
        reminder_description: str | None = None,
        due_date: str | None = None,
    ) -> AgentReminder:
        """
        Update a reminder for the given user. Only fields that are provided will be updated.

        Args:
            user_id: The user_id the reminder belongs to.
            reminder_id: The unique id of the reminder to update.
            reminder_description: New description for the reminder. If omitted, the existing description is kept.
            due_date: New due date in YYYY-MM-DD format. If omitted, the existing due date is kept.

        Raises:
            AgentReminderNotFoundError: If no reminder exists for the given user_id and reminder_id.

        Returns:
            The updated reminder.
        """
        collection = self.db[settings.AGENT_REMINDERS_COLLECTION_NAME]

        update_data = {}
        if reminder_description is not None:
            update_data["reminder_description"] = reminder_description

        if due_date is not None:
            update_data["due_date"] = due_date

        if not update_data:
            doc = await collection.find_one({"user_id": user_id, "reminder_id": reminder_id})
            if not doc:
                raise AgentReminderNotFoundError(f"Agent reminder not found for reminder_id: {reminder_id}")

            mongo_doc = AgentReminderMongoDoc.model_validate(doc)
            return AgentReminder(**mongo_doc.model_dump())

        updated_doc = await collection.find_one_and_update(
            {"user_id": user_id, "reminder_id": reminder_id},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER,
        )

        if not updated_doc:
            raise AgentReminderNotFoundError(f"Agent reminder not found for reminder_id: {reminder_id}")

        mongo_doc = AgentReminderMongoDoc.model_validate(updated_doc)
        return AgentReminder(
            user_id=mongo_doc.user_id,
            reminder_id=mongo_doc.reminder_id,
            reminder_description=mongo_doc.reminder_description,
            created_at=mongo_doc.created_at,
            due_date=mongo_doc.due_date,
        )
