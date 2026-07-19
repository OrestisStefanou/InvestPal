import asyncio
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
from repos.agent_reminders import AgentRemindersTable


class AgentReminderNotFoundError(Exception):
    pass


class AgentReminderService(ABC):
    @abstractmethod
    async def create_agent_reminder(
        self,
        reminder_description: str,
        due_date: str | None = None,
    ) -> AgentReminder:
        pass

    @abstractmethod
    async def get_agent_reminders(
        self,
    ) -> list[AgentReminder]:
        pass

    @abstractmethod
    async def delete_agent_reminder(
        self,
        reminder_id: str,
    ) -> None:
        pass

    @abstractmethod
    async def update_agent_reminder(
        self,
        reminder_id: str,
        reminder_description: str | None = None,
        due_date: str | None = None,
    ) -> AgentReminder:
        pass


class TursoAgentReminderService(AgentReminderService):
    def __init__(self, table: AgentRemindersTable):
        self._table = table

    async def create_agent_reminder(
        self,
        reminder_description: str,
        due_date: str | None = None,
    ) -> AgentReminder:
        row = await asyncio.to_thread(
            self._table.create_reminder,
            description=reminder_description,
            due_date=due_date,
        )
        return AgentReminder(
            id=row.id,
            description=row.description,
            created_at=row.created_at,
            due_date=row.due_date,
        )

    async def get_agent_reminders(
        self,
    ) -> list[AgentReminder]:
        rows = await asyncio.to_thread(self._table.get_reminders)
        return [
            AgentReminder(
                id=row.id,
                description=row.description,
                created_at=row.created_at,
                due_date=row.due_date,
            )
            for row in rows
        ]

    async def delete_agent_reminder(
        self,
        reminder_id: str,
    ) -> None:
        deleted = await asyncio.to_thread(self._table.delete_reminder, reminder_id)
        if not deleted:
            raise AgentReminderNotFoundError(f"Agent reminder not found for reminder_id: {reminder_id}")

    async def update_agent_reminder(
        self,
        reminder_id: str,
        reminder_description: str | None = None,
        due_date: str | None = None,
    ) -> AgentReminder:
        row = await asyncio.to_thread(
            self._table.update_reminder,
            reminder_id=reminder_id,
            description=reminder_description,
            due_date=due_date,
        )
        if not row:
            raise AgentReminderNotFoundError(f"Agent reminder not found for reminder_id: {reminder_id}")

        return AgentReminder(
            id=row.id,
            description=row.description,
            created_at=row.created_at,
            due_date=row.due_date,
        )


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
        reminder_description: str,
        due_date: str | None = None,
    ) -> AgentReminder:
        collection = self.db[settings.AGENT_REMINDERS_COLLECTION_NAME]
        reminder_id = str(uuid.uuid4())
        created_at = dt.datetime.now(dt.timezone.utc).isoformat()

        doc = AgentReminderMongoDoc(
            user_id="",
            reminder_id=reminder_id,
            reminder_description=reminder_description,
            created_at=created_at,
            due_date=due_date,
        )
        await collection.insert_one(doc.model_dump())

        return AgentReminder(
            id=reminder_id,
            description=reminder_description,
            created_at=created_at,
            due_date=due_date,
        )

    async def get_agent_reminders(
        self,
    ) -> list[AgentReminder]:
        collection = self.db[settings.AGENT_REMINDERS_COLLECTION_NAME]
        cursor = collection.find({})
        docs = await cursor.to_list(length=None)

        return [
            AgentReminder(
                id=doc["reminder_id"],
                description=doc["reminder_description"],
                created_at=doc["created_at"],
                due_date=doc.get("due_date"),
            )
            for doc in docs
        ]

    async def delete_agent_reminder(
        self,
        reminder_id: str,
    ) -> None:
        collection = self.db[settings.AGENT_REMINDERS_COLLECTION_NAME]
        result = await collection.delete_one({"reminder_id": reminder_id})
        if result.deleted_count == 0:
            raise AgentReminderNotFoundError(f"Agent reminder not found for reminder_id: {reminder_id}")

    async def update_agent_reminder(
        self,
        reminder_id: str,
        reminder_description: str | None = None,
        due_date: str | None = None,
    ) -> AgentReminder:
        collection = self.db[settings.AGENT_REMINDERS_COLLECTION_NAME]

        update_data = {}
        if reminder_description is not None:
            update_data["reminder_description"] = reminder_description

        if due_date is not None:
            update_data["due_date"] = due_date

        if not update_data:
            doc = await collection.find_one({"reminder_id": reminder_id})
            if not doc:
                raise AgentReminderNotFoundError(f"Agent reminder not found for reminder_id: {reminder_id}")

            mongo_doc = AgentReminderMongoDoc.model_validate(doc)
            return AgentReminder(
                id=mongo_doc.reminder_id,
                description=mongo_doc.reminder_description,
                created_at=mongo_doc.created_at,
                due_date=mongo_doc.due_date,
            )

        updated_doc = await collection.find_one_and_update(
            {"reminder_id": reminder_id},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER,
        )

        if not updated_doc:
            raise AgentReminderNotFoundError(f"Agent reminder not found for reminder_id: {reminder_id}")

        mongo_doc = AgentReminderMongoDoc.model_validate(updated_doc)
        return AgentReminder(
            id=mongo_doc.reminder_id,
            description=mongo_doc.reminder_description,
            created_at=mongo_doc.created_at,
            due_date=mongo_doc.due_date,
        )
