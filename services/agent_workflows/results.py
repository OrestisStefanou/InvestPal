import datetime as dt
import uuid
from abc import ABC, abstractmethod

from pydantic import BaseModel
from pymongo import AsyncMongoClient

from config import settings
from models.agent_workflow import WorkflowResult


class WorkflowResultService(ABC):
    @abstractmethod
    async def save_result(
        self,
        workflow_id: str,
        user_id: str,
        workflow_name: str,
        output: str,
    ) -> WorkflowResult:
        pass

    @abstractmethod
    async def get_results(self, user_id: str) -> list[WorkflowResult]:
        pass


class WorkflowResultMongoDoc(BaseModel):
    result_id: str
    workflow_id: str
    user_id: str
    workflow_name: str
    output: str
    ran_at: str


class MongoDBWorkflowResultService(WorkflowResultService):
    def __init__(self, mongo_client: AsyncMongoClient):
        self.db = mongo_client[settings.MONGO_DB_NAME]

    def _doc_to_model(self, doc: dict) -> WorkflowResult:
        return WorkflowResult(
            result_id=doc["result_id"],
            workflow_id=doc["workflow_id"],
            user_id=doc["user_id"],
            workflow_name=doc["workflow_name"],
            output=doc["output"],
            ran_at=doc["ran_at"],
        )

    async def save_result(
        self,
        workflow_id: str,
        user_id: str,
        workflow_name: str,
        output: str,
    ) -> WorkflowResult:
        result_id = str(uuid.uuid4())
        ran_at = dt.datetime.now(dt.timezone.utc).isoformat()
        doc = WorkflowResultMongoDoc(
            result_id=result_id,
            workflow_id=workflow_id,
            user_id=user_id,
            workflow_name=workflow_name,
            output=output,
            ran_at=ran_at,
        )
        collection = self.db[settings.WORKFLOW_RESULTS_COLLECTION_NAME]
        await collection.insert_one(doc.model_dump())
        return self._doc_to_model(doc.model_dump())

    async def get_results(self, user_id: str) -> list[WorkflowResult]:
        collection = self.db[settings.WORKFLOW_RESULTS_COLLECTION_NAME]
        cursor = collection.find({"user_id": user_id}).sort("ran_at", -1)
        docs = await cursor.to_list(length=None)
        return [self._doc_to_model(doc) for doc in docs]
