import datetime as dt
import uuid
from abc import ABC, abstractmethod

from croniter import croniter
from pydantic import BaseModel
from pymongo import AsyncMongoClient, ReturnDocument

from config import settings
from models.agent_workflow import AgentWorkflow
from services.user_context import UserContextNotFoundError


class AgentWorkflowNotFoundError(Exception):
    pass


class AgentWorkflowService(ABC):
    @abstractmethod
    async def create_workflow(
        self,
        user_id: str,
        name: str,
        instructions: str,
        schedule: str,
    ) -> AgentWorkflow:
        pass

    @abstractmethod
    async def get_workflows(self, user_id: str) -> list[AgentWorkflow]:
        pass

    @abstractmethod
    async def claim_next_due_workflow(self) -> AgentWorkflow | None:
        """Atomically find one due workflow, mark it as 'running', and return it."""
        pass

    @abstractmethod
    async def release_workflow_lock(self, workflow_id: str) -> None:
        """Release the running lock by setting status back to 'active'."""
        pass

    @abstractmethod
    async def update_workflow(
        self,
        user_id: str,
        workflow_id: str,
        name: str | None = None,
        instructions: str | None = None,
        schedule: str | None = None,
        status: str | None = None,
    ) -> AgentWorkflow:
        pass

    @abstractmethod
    async def delete_workflow(self, user_id: str, workflow_id: str) -> None:
        pass

    @abstractmethod
    async def mark_workflow_ran(self, workflow_id: str, ran_at: str) -> None:
        """Update last_run_at, compute next_run_at from schedule, and reset status to 'active'."""
        pass


class AgentWorkflowMongoDoc(BaseModel):
    workflow_id: str
    user_id: str
    name: str
    instructions: str
    schedule: str
    status: str
    created_at: str
    last_run_at: str | None = None
    next_run_at: str | None = None


class MongoDBAgentWorkflowService(AgentWorkflowService):
    def __init__(self, mongo_client: AsyncMongoClient):
        self.db = mongo_client[settings.MONGO_DB_NAME]

    def _compute_next_run_at(self, schedule: str, base: dt.datetime) -> str:
        cron = croniter(schedule, base)
        return cron.get_next(dt.datetime).isoformat()

    def _doc_to_model(self, doc: dict) -> AgentWorkflow:
        return AgentWorkflow(
            workflow_id=doc["workflow_id"],
            user_id=doc["user_id"],
            name=doc["name"],
            instructions=doc["instructions"],
            schedule=doc["schedule"],
            status=doc["status"],
            created_at=doc["created_at"],
            last_run_at=doc.get("last_run_at"),
            next_run_at=doc.get("next_run_at"),
        )

    async def create_workflow(
        self,
        user_id: str,
        name: str,
        instructions: str,
        schedule: str,
    ) -> AgentWorkflow:
        user_context_collection = self.db[settings.USER_CONTEXT_COLLECTION_NAME]
        if not await user_context_collection.find_one({"user_id": user_id}):
            raise UserContextNotFoundError(f"User context not found for user_id: {user_id}")

        now = dt.datetime.now(dt.timezone.utc)
        workflow_id = str(uuid.uuid4())
        next_run_at = self._compute_next_run_at(schedule, now)

        doc = AgentWorkflowMongoDoc(
            workflow_id=workflow_id,
            user_id=user_id,
            name=name,
            instructions=instructions,
            schedule=schedule,
            status="active",
            created_at=now.isoformat(),
            next_run_at=next_run_at,
        )
        collection = self.db[settings.AGENT_WORKFLOWS_COLLECTION_NAME]
        await collection.insert_one(doc.model_dump())
        return self._doc_to_model(doc.model_dump())

    async def get_workflows(self, user_id: str) -> list[AgentWorkflow]:
        collection = self.db[settings.AGENT_WORKFLOWS_COLLECTION_NAME]
        cursor = collection.find({"user_id": user_id})
        docs = await cursor.to_list(length=None)
        return [self._doc_to_model(doc) for doc in docs]

    async def claim_next_due_workflow(self) -> AgentWorkflow | None:
        now = dt.datetime.now(dt.timezone.utc).isoformat()
        collection = self.db[settings.AGENT_WORKFLOWS_COLLECTION_NAME]
        doc = await collection.find_one_and_update(
            {
                "status": "active",
                "next_run_at": {"$lte": now},
            },
            {"$set": {"status": "running"}},
            return_document=ReturnDocument.AFTER,
        )
        return self._doc_to_model(doc) if doc else None

    async def release_workflow_lock(self, workflow_id: str) -> None:
        collection = self.db[settings.AGENT_WORKFLOWS_COLLECTION_NAME]
        await collection.update_one(
            {"workflow_id": workflow_id, "status": "running"},
            {"$set": {"status": "active"}}
        )

    async def update_workflow(
        self,
        user_id: str,
        workflow_id: str,
        name: str | None = None,
        instructions: str | None = None,
        schedule: str | None = None,
        status: str | None = None,
    ) -> AgentWorkflow:
        collection = self.db[settings.AGENT_WORKFLOWS_COLLECTION_NAME]
        update_data: dict = {}
        if name is not None:
            update_data["name"] = name
        if instructions is not None:
            update_data["instructions"] = instructions
        if status is not None:
            update_data["status"] = status
        if schedule is not None:
            update_data["schedule"] = schedule
            now = dt.datetime.now(dt.timezone.utc)
            update_data["next_run_at"] = self._compute_next_run_at(schedule, now)

        if not update_data:
            doc = await collection.find_one({"user_id": user_id, "workflow_id": workflow_id})
            if not doc:
                raise AgentWorkflowNotFoundError(f"Workflow not found: {workflow_id}")
            return self._doc_to_model(doc)

        updated = await collection.find_one_and_update(
            {"user_id": user_id, "workflow_id": workflow_id},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER,
        )
        if not updated:
            raise AgentWorkflowNotFoundError(f"Workflow not found: {workflow_id}")
        return self._doc_to_model(updated)

    async def delete_workflow(self, user_id: str, workflow_id: str) -> None:
        collection = self.db[settings.AGENT_WORKFLOWS_COLLECTION_NAME]
        result = await collection.delete_one({"user_id": user_id, "workflow_id": workflow_id})
        if result.deleted_count == 0:
            raise AgentWorkflowNotFoundError(f"Workflow not found: {workflow_id}")

    async def mark_workflow_ran(self, workflow_id: str, ran_at: str) -> None:
        collection = self.db[settings.AGENT_WORKFLOWS_COLLECTION_NAME]
        doc = await collection.find_one({"workflow_id": workflow_id})
        if not doc:
            raise AgentWorkflowNotFoundError(f"Workflow not found: {workflow_id}")

        base = dt.datetime.fromisoformat(ran_at)
        next_run_at = self._compute_next_run_at(doc["schedule"], base)
        await collection.update_one(
            {"workflow_id": workflow_id},
            {"$set": {
                "last_run_at": ran_at,
                "next_run_at": next_run_at,
                "status": "active"
            }},
        )
