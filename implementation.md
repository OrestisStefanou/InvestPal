# Implementation Guide — Agent Scheduled Workflows

Follow the steps below in order. Each step specifies the exact file to create or modify and
the exact code to write.

---

## Step 0 — Add dependency

```bash
uv add croniter
```

---

## Step 1 — Add new collection name settings

**File:** `config.py`

Add two new fields to the `Settings` class alongside the existing collection name fields:

```python
AGENT_WORKFLOWS_COLLECTION_NAME: str = "agent_workflows"
WORKFLOW_RESULTS_COLLECTION_NAME: str = "workflow_results"
```

---

## Step 2 — Create models

**File:** `models/agent_workflow.py` (new file)

```python
from pydantic import BaseModel, Field


class AgentWorkflow(BaseModel):
    workflow_id: str = Field(description="Unique id of the workflow")
    user_id: str = Field(description="The user this workflow belongs to")
    name: str = Field(description="Human-readable name for the workflow")
    instructions: str = Field(description="The instructions the agent will execute on each run")
    schedule: str = Field(description="Cron expression, e.g. '0 0 1 * *' for monthly")
    status: str = Field(description="'active' or 'paused'")
    created_at: str = Field(description="ISO 8601 creation timestamp")
    last_run_at: str | None = Field(default=None, description="ISO 8601 timestamp of last run")
    next_run_at: str | None = Field(default=None, description="ISO 8601 timestamp of next scheduled run")


class WorkflowResult(BaseModel):
    result_id: str = Field(description="Unique id of this result")
    workflow_id: str = Field(description="The workflow that produced this result")
    user_id: str = Field(description="The user this result belongs to")
    workflow_name: str = Field(description="Name of the workflow at time of execution")
    output: str = Field(description="The agent's report for this run")
    ran_at: str = Field(description="ISO 8601 timestamp of when the workflow ran")
```

---

## Step 3 — Create the agent_workflows package

Create the directory `services/agent_workflows/` with the following four files.

---

### `services/agent_workflows/__init__.py`

Exports all public symbols so the rest of the codebase imports from
`services.agent_workflows` without needing to know the internal file structure.

```python
from services.agent_workflows.service import (
    AgentWorkflowService,
    MongoDBAgentWorkflowService,
    AgentWorkflowNotFoundError,
)
from services.agent_workflows.results import (
    WorkflowResultService,
    MongoDBWorkflowResultService,
)
from services.agent_workflows.notifier import (
    WorkflowNotifier,
    MongoDBWorkflowNotifier,
)
from services.agent_workflows.runner import WorkflowRunner
```

---

### `services/agent_workflows/service.py`

```python
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
```

---

### `services/agent_workflows/results.py`

```python
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
```

---

### `services/agent_workflows/notifier.py`

```python
from abc import ABC, abstractmethod

from models.agent_workflow import WorkflowResult
from services.agent_workflows.results import WorkflowResultService


class WorkflowNotifier(ABC):
    @abstractmethod
    async def notify(self, result: WorkflowResult) -> None:
        pass


class MongoDBWorkflowNotifier(WorkflowNotifier):
    """v1 notifier — persists results to MongoDB only."""

    def __init__(self, workflow_result_service: WorkflowResultService):
        self._workflow_result_service = workflow_result_service

    async def notify(self, result: WorkflowResult) -> None:
        await self._workflow_result_service.save_result(
            workflow_id=result.workflow_id,
            user_id=result.user_id,
            workflow_name=result.workflow_name,
            output=result.output,
        )
```

---

### `services/agent_workflows/runner.py`

```python
import datetime as dt
import logging

from models.agent_workflow import WorkflowResult
from models.session import Message, MessageRole
from services.agent_workflows.service import AgentWorkflowService
from services.agent_workflows.notifier import WorkflowNotifier
from services.agent_workflows.results import WorkflowResultService
from services.agents.agent import (
    WorkflowExecutionAgent,
    WorkflowExecutionPromptVars,
    InvestmentManagerRuntimeContext,
)
from services.agent_reminder import AgentReminderService
from services.user_context import UserContextService, UserContextNotFoundError

logger = logging.getLogger(__name__)


class WorkflowRunner:
    def __init__(
        self,
        workflow_execution_agent: WorkflowExecutionAgent,
        agent_workflow_service: AgentWorkflowService,
        workflow_result_service: WorkflowResultService,
        user_context_service: UserContextService,
        agent_reminder_service: AgentReminderService,
        notifier: WorkflowNotifier,
    ):
        self._agent = workflow_execution_agent
        self._workflow_service = agent_workflow_service
        self._workflow_result_service = workflow_result_service
        self._user_context_service = user_context_service
        self._agent_reminder_service = agent_reminder_service
        self._notifier = notifier

    async def run_due_workflows(self) -> None:
        while True:
            workflow = await self._workflow_service.claim_next_due_workflow()
            if not workflow:
                break
            try:
                await self._run_workflow(workflow)
            except Exception:
                logger.exception(
                    "Failed to run workflow %s for user %s",
                    workflow.workflow_id,
                    workflow.user_id,
                )
                await self._workflow_service.release_workflow_lock(workflow.workflow_id)

    async def _run_workflow(self, workflow) -> None:
        user_context = await self._user_context_service.get_user_context(workflow.user_id)
        if not user_context:
            raise UserContextNotFoundError(f"User context not found for user_id: {workflow.user_id}")

        # Single-turn synthetic conversation — no history, just the workflow instructions
        conversation = [Message(role=MessageRole.USER, content=workflow.instructions)]

        runtime_context = InvestmentManagerRuntimeContext(
            user_context_service=self._user_context_service,
            agent_reminder_service=self._agent_reminder_service,
            agent_workflow_service=self._workflow_service,
            workflow_result_service=self._workflow_result_service,
        )

        agent_response = await self._agent.generate_response(
            conversation=conversation,
            runtime_context=runtime_context,
            system_prompt_placeholder_values=WorkflowExecutionPromptVars(
                client_profile=user_context.model_dump(),
            ),
        )

        ran_at = dt.datetime.now(dt.timezone.utc).isoformat()

        result = WorkflowResult(
            result_id="",  # generated by save_result
            workflow_id=workflow.workflow_id,
            user_id=workflow.user_id,
            workflow_name=workflow.name,
            output=agent_response.response,
            ran_at=ran_at,
        )
        await self._notifier.notify(result)
        await self._workflow_service.mark_workflow_ran(workflow.workflow_id, ran_at)
```

---

## Step 4 — Add the workflow tools

**File:** `services/agents/tools.py`

### 4a. Add new imports at the top

```python
from models.agent_workflow import AgentWorkflow, WorkflowResult
from services.agent_workflows.service import AgentWorkflowService
from services.agent_workflows.results import WorkflowResultService
```

### 4b. Add a new runtime context dataclass (alongside the existing ones)

```python
@dataclass
class AgentWorkflowToolsRuntimeContext:
    agent_workflow_service: AgentWorkflowService
    workflow_result_service: WorkflowResultService
```

### 4c. Add the five new tool functions at the end of the file

```python
class CreateAgentWorkflowToolInput(BaseModel):
    user_id: str = Field(description="The id of the user to create the workflow for")
    name: str = Field(description="A short human-readable name for the workflow")
    instructions: str = Field(description="The full instructions the agent will execute on each scheduled run")
    schedule: str = Field(description="Cron expression for the schedule, e.g. '0 0 1 * *' for monthly on the 1st")


@tool(
    "createAgentWorkflow",
    args_schema=CreateAgentWorkflowToolInput,
    description="Create a new scheduled workflow for the user. The agent will execute the given instructions autonomously on the given schedule.",
)
async def create_agent_workflow(
    runtime: ToolRuntime[AgentWorkflowToolsRuntimeContext],
    user_id: str,
    name: str,
    instructions: str,
    schedule: str,
) -> AgentWorkflow:
    return await runtime.context.agent_workflow_service.create_workflow(
        user_id=user_id,
        name=name,
        instructions=instructions,
        schedule=schedule,
    )


@tool("getAgentWorkflows")
async def get_agent_workflows(
    runtime: ToolRuntime[AgentWorkflowToolsRuntimeContext],
    user_id: str,
) -> list[AgentWorkflow]:
    """Get all scheduled workflows for the given user.

    Args:
        user_id: The id of the user to get workflows for
    """
    return await runtime.context.agent_workflow_service.get_workflows(user_id=user_id)


class UpdateAgentWorkflowToolInput(BaseModel):
    user_id: str = Field(description="The id of the user the workflow belongs to")
    workflow_id: str = Field(description="The unique id of the workflow to update")
    name: str | None = Field(default=None, description="New name. If omitted, existing name is kept.")
    instructions: str | None = Field(default=None, description="New instructions. If omitted, existing instructions are kept.")
    schedule: str | None = Field(default=None, description="New cron schedule. If omitted, existing schedule is kept.")
    status: str | None = Field(default=None, description="New status: 'active' or 'paused'. If omitted, existing status is kept.")


@tool(
    "updateAgentWorkflow",
    args_schema=UpdateAgentWorkflowToolInput,
    description="Update an existing scheduled workflow. Only fields provided will be changed.",
)
async def update_agent_workflow(
    runtime: ToolRuntime[AgentWorkflowToolsRuntimeContext],
    user_id: str,
    workflow_id: str,
    name: str | None = None,
    instructions: str | None = None,
    schedule: str | None = None,
    status: str | None = None,
) -> AgentWorkflow:
    return await runtime.context.agent_workflow_service.update_workflow(
        user_id=user_id,
        workflow_id=workflow_id,
        name=name,
        instructions=instructions,
        schedule=schedule,
        status=status,
    )


class DeleteAgentWorkflowToolInput(BaseModel):
    user_id: str = Field(description="The id of the user the workflow belongs to")
    workflow_id: str = Field(description="The unique id of the workflow to delete")


@tool(
    "deleteAgentWorkflow",
    args_schema=DeleteAgentWorkflowToolInput,
    description="Delete a scheduled workflow for the user.",
)
async def delete_agent_workflow(
    runtime: ToolRuntime[AgentWorkflowToolsRuntimeContext],
    user_id: str,
    workflow_id: str,
) -> None:
    await runtime.context.agent_workflow_service.delete_workflow(
        user_id=user_id,
        workflow_id=workflow_id,
    )


class GetWorkflowResultsToolInput(BaseModel):
    user_id: str = Field(description="The id of the user to get workflow results for")


@tool(
    "getWorkflowResults",
    args_schema=GetWorkflowResultsToolInput,
    description="Get the results of all past workflow runs for the user, ordered by most recent first. Use this when the user asks what the agent has done on their behalf since the last conversation.",
)
async def get_workflow_results(
    runtime: ToolRuntime[AgentWorkflowToolsRuntimeContext],
    user_id: str,
) -> list[WorkflowResult]:
    return await runtime.context.workflow_result_service.get_results(user_id=user_id)
```

---

## Step 5 — Add the workflow execution prompt

**File:** `services/agents/prompts.py`

Append the following new prompt constant at the end of the file:

```python
WORKFLOW_EXECUTION_AGENT_PROMPT = """
You are an autonomous investment management agent executing a scheduled workflow on behalf
of a client with the following profile:

{client_profile}

You have been activated by a scheduled workflow — there is no live user in this conversation.
Your sole objective is to execute the given instructions completely and produce a clear report
of what you did and the outcome.

You MUST follow all instructions below:

---

## 1. EXECUTION RULES

- Execute the task fully and autonomously. Do NOT ask clarifying questions.
- Do NOT greet the user or produce any conversational filler.
- Use your tools freely — fetch market data, execute trades, run analysis, whatever the task requires.
- When performing structured analysis, use `getSkillNames` and `getSkill` to retrieve the
  relevant analytical skill and follow it.

---

## 2. ADJUST TO CLIENT PROFILE

Tailor the execution to the client's profile (risk tolerance, goals, knowledge level, portfolio).
The client profile above is your source of truth.

---

## 3. REPORT FORMAT

When the task is complete, produce a concise report covering:
- What you did
- The outcome or result
- Any notable observations or recommendations for the client's next review

Keep the report professional and factual. The client will read it asynchronously.

---

## 4. RESPONSE FORMAT

NEVER share your chain of thought or internal reasoning in the response. Only output the
final report.
"""
```

---

## Step 6 — Add `WorkflowExecutionAgent` to the agent module

**File:** `services/agents/agent.py`

### 6a. Add new imports

Add to the existing imports:

```python
from services.agent_workflows.service import AgentWorkflowService
from services.agent_workflows.results import WorkflowResultService
from services.agents.prompts import WORKFLOW_EXECUTION_AGENT_PROMPT
from services.agents.tools import (
    AgentWorkflowToolsRuntimeContext,
    create_agent_workflow,
    get_agent_workflows,
    update_agent_workflow,
    delete_agent_workflow,
    get_workflow_results,
)
```

### 6b. Extend `InvestmentManagerRuntimeContext`

Replace the existing `InvestmentManagerRuntimeContext` dataclass:

```python
@dataclass
class InvestmentManagerRuntimeContext(
    UserContextToolsRuntimeContext,
    AgentReminderToolsRuntimeContext,
    AgentWorkflowToolsRuntimeContext,
):
    pass
```

### 6c. Add workflow tools to `InvestmentManagerAgent.create()`

Inside the `create` classmethod, add the five new tools to the `tools` list:

```python
tools = [
    get_current_datetime,
    get_user_conversation_notes,
    create_agent_reminder,
    get_agent_reminders,
    update_agent_reminder,
    delete_agent_reminder,
    create_agent_workflow,       # new
    get_agent_workflows,         # new
    update_agent_workflow,       # new
    delete_agent_workflow,       # new
    get_workflow_results,        # new
    get_skill_names,
    get_skill,
    add,
    subtract,
    multiply,
    divide,
]
```

### 6d. Add `WorkflowExecutionAgent` at the end of the file

```python
class WorkflowExecutionAgentResponse(BaseModel):
    response: str


class WorkflowExecutionPromptVars(TypedDict):
    client_profile: dict[str, Any]


class WorkflowExecutionAgent(Agent):
    """
    Non-conversational agent that executes scheduled workflows autonomously.
    Uses the same tools and runtime context as InvestmentManagerAgent but with
    a purpose-built prompt that suppresses conversational behaviour.
    Note: Callers should use the create classmethod to instantiate.
    """

    def __init__(
        self,
        tools: list[BaseTool],
        middleware: list[AgentMiddleware],
    ):
        super().__init__(
            tools=tools,
            response_format=WorkflowExecutionAgentResponse,
            system_prompt=WORKFLOW_EXECUTION_AGENT_PROMPT,
            middleware=middleware,
            runtime_context_schema=InvestmentManagerRuntimeContext,
            provider=settings.INVESTMENT_MANAGER_LLM_PROVIDER,
            model_name=settings.INVESTMENT_MANAGER_LLM_MODEL,
            temperature=settings.INVESTMENT_MANAGER_TEMPERATURE,
        )

    async def generate_response(
        self,
        conversation: list[Message],
        runtime_context: InvestmentManagerRuntimeContext,
        system_prompt_placeholder_values: WorkflowExecutionPromptVars | None = None,
    ) -> WorkflowExecutionAgentResponse:
        return await super().generate_response(
            conversation=conversation,
            runtime_context=runtime_context,
            system_prompt_placeholder_values=system_prompt_placeholder_values,
        )

    @classmethod
    async def create(
        cls,
        mcp_client: MultiServerMCPClient,
        middleware: list[AgentMiddleware],
    ) -> "WorkflowExecutionAgent":
        tools = [
            get_current_datetime,
            get_user_conversation_notes,
            create_agent_reminder,
            get_agent_reminders,
            update_agent_reminder,
            delete_agent_reminder,
            create_agent_workflow,
            get_agent_workflows,
            update_agent_workflow,
            delete_agent_workflow,
            get_workflow_results,
            get_skill_names,
            get_skill,
            add,
            subtract,
            multiply,
            divide,
        ]
        if settings.MARKET_DATA_MCP_SERVER_URL:
            market_data_tools = await mcp_client.get_tools(server_name=settings.MARKET_DATA_MCP_SERVER_NAME)
            tools.extend(market_data_tools)

        if settings.ALPACA_MCP_SERVER_URL:
            alpaca_tools = await mcp_client.get_tools(server_name=settings.ALPACA_MCP_SERVER_NAME)
            tools.extend(alpaca_tools)

        if settings.COINBASE_MCP_SERVER_URL:
            coinbase_tools = await mcp_client.get_tools(server_name=settings.COINBASE_MCP_SERVER_NAME)
            tools.extend(coinbase_tools)

        return cls(tools=tools, middleware=middleware)
```

---

## Step 7 — Update `InvestmentManagerAgentService`

**File:** `services/agent_service.py`

### 7a. Add new imports

```python
from services.agent_workflows.service import AgentWorkflowService
from services.agent_workflows.results import WorkflowResultService
```

### 7b. Update `__init__` to accept the two new services

```python
def __init__(
    self,
    investment_manager_agent: InvestmentManagerAgent,
    user_context_memory_manager_agent: UserContextMemoryManagerAgent,
    user_context_service: UserContextService,
    agent_reminder_service: AgentReminderService,
    agent_workflow_service: AgentWorkflowService,
    workflow_result_service: WorkflowResultService,
):
    self._investment_manager_agent = investment_manager_agent
    self._user_context_memory_manager_agent = user_context_memory_manager_agent
    self._user_context_service = user_context_service
    self._agent_reminder_service = agent_reminder_service
    self._agent_workflow_service = agent_workflow_service
    self._workflow_result_service = workflow_result_service
```

### 7c. Update the runtime context inside `generate_agent_text_response`

Replace the `InvestmentManagerRuntimeContext(...)` call:

```python
runtime_context=InvestmentManagerRuntimeContext(
    user_context_service=self._user_context_service,
    agent_reminder_service=self._agent_reminder_service,
    agent_workflow_service=self._agent_workflow_service,
    workflow_result_service=self._workflow_result_service,
),
```

---

## Step 8 — Create the REST API router

**File:** `apps/rest_api/agent_workflows.py` (new file)

```python
import http

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from dependencies import (
    get_agent_workflow_service,
    get_workflow_result_service,
    get_workflow_runner,
)
from services.agent_workflows import (
    AgentWorkflowService,
    AgentWorkflowNotFoundError,
    WorkflowResultService,
    WorkflowRunner,
)
from services.user_context import UserContextNotFoundError

router = APIRouter()


class AgentWorkflowSchema(BaseModel):
    workflow_id: str
    user_id: str
    name: str
    instructions: str
    schedule: str
    status: str
    created_at: str
    last_run_at: str | None = None
    next_run_at: str | None = None


class CreateAgentWorkflowRequest(BaseModel):
    user_id: str
    name: str
    instructions: str
    schedule: str


class UpdateAgentWorkflowRequest(BaseModel):
    name: str | None = None
    instructions: str | None = None
    schedule: str | None = None
    status: str | None = None


class WorkflowResultSchema(BaseModel):
    result_id: str
    workflow_id: str
    user_id: str
    workflow_name: str
    output: str
    ran_at: str


@router.post("/workflows", response_model=AgentWorkflowSchema, status_code=http.HTTPStatus.CREATED)
async def create_workflow(
    body: CreateAgentWorkflowRequest,
    service: AgentWorkflowService = Depends(get_agent_workflow_service),
):
    try:
        workflow = await service.create_workflow(
            user_id=body.user_id,
            name=body.name,
            instructions=body.instructions,
            schedule=body.schedule,
        )
    except UserContextNotFoundError as e:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail=str(e))
    return AgentWorkflowSchema(**workflow.model_dump())


@router.get("/workflows/{user_id}", response_model=list[AgentWorkflowSchema])
async def get_workflows(
    user_id: str,
    service: AgentWorkflowService = Depends(get_agent_workflow_service),
):
    workflows = await service.get_workflows(user_id=user_id)
    return [AgentWorkflowSchema(**w.model_dump()) for w in workflows]


@router.patch("/workflows/{user_id}/{workflow_id}", response_model=AgentWorkflowSchema)
async def update_workflow(
    user_id: str,
    workflow_id: str,
    body: UpdateAgentWorkflowRequest,
    service: AgentWorkflowService = Depends(get_agent_workflow_service),
):
    try:
        workflow = await service.update_workflow(
            user_id=user_id,
            workflow_id=workflow_id,
            name=body.name,
            instructions=body.instructions,
            schedule=body.schedule,
            status=body.status,
        )
    except AgentWorkflowNotFoundError as e:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail=str(e))
    return AgentWorkflowSchema(**workflow.model_dump())


@router.delete("/workflows/{user_id}/{workflow_id}", status_code=http.HTTPStatus.NO_CONTENT)
async def delete_workflow(
    user_id: str,
    workflow_id: str,
    service: AgentWorkflowService = Depends(get_agent_workflow_service),
):
    try:
        await service.delete_workflow(user_id=user_id, workflow_id=workflow_id)
    except AgentWorkflowNotFoundError as e:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail=str(e))


@router.post("/workflows/check-and-run", status_code=http.HTTPStatus.NO_CONTENT)
async def check_and_run_workflows(
    runner: WorkflowRunner = Depends(get_workflow_runner),
):
    """Heartbeat endpoint called by an external cron job. Runs all due workflows."""
    await runner.run_due_workflows()


@router.get("/workflow_results/{user_id}", response_model=list[WorkflowResultSchema])
async def get_workflow_results(
    user_id: str,
    service: WorkflowResultService = Depends(get_workflow_result_service),
):
    results = await service.get_results(user_id=user_id)
    return [WorkflowResultSchema(**r.model_dump()) for r in results]
```

---

## Step 9 — Update dependencies.py

**File:** `dependencies.py`

### 9a. Add new imports

```python
from services.agent_workflows import (
    AgentWorkflowService,
    MongoDBAgentWorkflowService,
    WorkflowResultService,
    MongoDBWorkflowResultService,
    WorkflowNotifier,
    MongoDBWorkflowNotifier,
    WorkflowRunner,
)
from services.agents.agent import WorkflowExecutionAgent
```

### 9b. Add four new dependency functions (append to end of file)

```python
def get_agent_workflow_service(
    db_client: AsyncMongoClient = Depends(get_db_client),
) -> AgentWorkflowService:
    return MongoDBAgentWorkflowService(mongo_client=db_client)


def get_workflow_result_service(
    db_client: AsyncMongoClient = Depends(get_db_client),
) -> WorkflowResultService:
    return MongoDBWorkflowResultService(mongo_client=db_client)


def get_workflow_notifier(
    workflow_result_service: WorkflowResultService = Depends(get_workflow_result_service),
) -> WorkflowNotifier:
    return MongoDBWorkflowNotifier(workflow_result_service=workflow_result_service)


async def get_workflow_runner(
    mcp_client: MultiServerMCPClient = Depends(get_mcp_client),
    agent_workflow_service: AgentWorkflowService = Depends(get_agent_workflow_service),
    workflow_result_service: WorkflowResultService = Depends(get_workflow_result_service),
    user_context_service: UserContextService = Depends(get_user_context_service),
    agent_reminder_service: AgentReminderService = Depends(get_agent_reminder_service),
    notifier: WorkflowNotifier = Depends(get_workflow_notifier),
) -> WorkflowRunner:
    agent = await WorkflowExecutionAgent.create(
        mcp_client=mcp_client,
        middleware=[ToolErrorMiddleware(), ToolLoggingMiddleware()],
    )
    return WorkflowRunner(
        workflow_execution_agent=agent,
        agent_workflow_service=agent_workflow_service,
        workflow_result_service=workflow_result_service,
        user_context_service=user_context_service,
        agent_reminder_service=agent_reminder_service,
        notifier=notifier,
    )
```

### 9c. Update `get_investment_manager_agent_service`

```python
def get_investment_manager_agent_service(
    investment_manager_agent: InvestmentManagerAgent = Depends(get_investment_manager_agent),
    user_context_memory_manager_agent: UserContextMemoryManagerAgent = Depends(get_user_context_memory_manager_agent),
    user_context_service: UserContextService = Depends(get_user_context_service),
    agent_reminder_service: AgentReminderService = Depends(get_agent_reminder_service),
    agent_workflow_service: AgentWorkflowService = Depends(get_agent_workflow_service),
    workflow_result_service: WorkflowResultService = Depends(get_workflow_result_service),
) -> InvestmentManagerAgentService:
    return InvestmentManagerAgentService(
        investment_manager_agent=investment_manager_agent,
        user_context_memory_manager_agent=user_context_memory_manager_agent,
        user_context_service=user_context_service,
        agent_reminder_service=agent_reminder_service,
        agent_workflow_service=agent_workflow_service,
        workflow_result_service=workflow_result_service,
    )
```

---

## Step 10 — Register the router in main.py

**File:** `main.py`

### 10a. Add the import

```python
from apps.rest_api import (
    session,
    user_context,
    chat,
    agent_reminders,
    agent_workflows,   # new
)
```

### 10b. Register the router

```python
app.include_router(agent_workflows.router)
```

---

## Summary of new and changed files

| File | Action |
|------|--------|
| `models/agent_workflow.py` | Create — `AgentWorkflow` and `WorkflowResult` models |
| `services/agent_workflows/__init__.py` | Create — package exports |
| `services/agent_workflows/service.py` | Create — `AgentWorkflowService` + MongoDB impl |
| `services/agent_workflows/results.py` | Create — `WorkflowResultService` + MongoDB impl |
| `services/agent_workflows/notifier.py` | Create — `WorkflowNotifier` + `MongoDBWorkflowNotifier` |
| `services/agent_workflows/runner.py` | Create — `WorkflowRunner` |
| `apps/rest_api/agent_workflows.py` | Create — REST endpoints |
| `config.py` | Add 2 collection name settings |
| `services/agents/tools.py` | Add `AgentWorkflowToolsRuntimeContext` + 5 new tools |
| `services/agents/agent.py` | Extend `InvestmentManagerRuntimeContext`, add tools to `InvestmentManagerAgent`, add `WorkflowExecutionAgent` |
| `services/agents/prompts.py` | Add `WORKFLOW_EXECUTION_AGENT_PROMPT` |
| `services/agent_service.py` | Accept + forward 2 new services in runtime context |
| `dependencies.py` | Add 4 new dependency functions, update existing one |
| `main.py` | Register new router |

## New API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/workflows` | Create a workflow |
| `GET` | `/workflows/{user_id}` | List workflows for a user |
| `PATCH` | `/workflows/{user_id}/{workflow_id}` | Update a workflow |
| `DELETE` | `/workflows/{user_id}/{workflow_id}` | Delete a workflow |
| `POST` | `/workflows/check-and-run` | Heartbeat — runs all due workflows |
| `GET` | `/workflow_results/{user_id}` | Fetch past workflow results |
