# Task
Create agent scheduled workflows

## What is a scheduled agent worfklow from a user prespective
Imagine the following scenario:
A user says to the investment manager 'I want you to invest for me 500 euros every month wherever you think it's best given my profile'. The agent should reply with something like 'sure i will create a workflow for you' (maybe ask any clarification questions along the way). The backend will trigger these workflows based on the created schedule and the agent will invest 500 euros every month for the user and will just report back to the user where it invested the money.

Another example scenario:
A user says to the investment manager 'Every week I would like you to do some market research and reccommend me some actions that will help me reach my investment goals'.
The agent could respond with some clarification questions and at the end it will create a scheduled workflow to perform what the user asked every week.


## What is a scheduled workflow from a system's perspective

### Data Model — `agent_workflows` MongoDB collection

```python
{
    "workflow_id": str,       # UUID
    "user_id": str,
    "name": str,              # e.g. "Monthly Investment"
    "prompt": str,            # Instruction to execute: "Invest 500€ wherever you think best given my profile"
    "schedule": str,          # Cron expression: "0 0 1 * *"
    "status": str,            # "active" | "paused"
    "created_at": str,        # ISO 8601
    "last_run_at": str | None,
    "next_run_at": str | None
}
```

### Agent Tools

Four new tools added to the InvestmentManagerAgent, mirroring the existing reminder pattern:
- `createAgentWorkflow(user_id, name, prompt, schedule)`
- `getAgentWorkflows(user_id)`
- `updateAgentWorkflow(workflow_id, ...)`
- `deleteAgentWorkflow(workflow_id)`

When a user makes a request like "invest 500€ every month", the agent gathers any needed info,
calls `createAgentWorkflow`, confirms with the user, and the workflow is persisted.

### Execution Layer

An external cron job acts as a dumb heartbeat — it calls `POST /workflows/check-and-run` on a
fixed interval (e.g. every hour). The backend logic inspects `next_run_at` across all active
workflows and only executes those that are due. This means:
- The cron job can be called any number of times without double-running a workflow
- Workflows can be paused/resumed without touching the scheduler
- The `schedule` field (cron expression) is the source of truth; it is used to compute
  `next_run_at` after each successful run

### Workflow Execution Flow

```
POST /workflows/check-and-run (called by external heartbeat)
    → Query all active workflows where next_run_at <= now
    → For each due workflow:
        → Load user_context
        → Construct synthetic conversation (no history)
        → Run InvestmentManagerAgent
        → Store result via WorkflowNotifier
        → Update workflow.last_run_at and compute next_run_at from schedule
```

The synthetic conversation passed to the agent has no history. It contains a single framing
message that signals autonomous execution mode:

> "You are executing a scheduled workflow on behalf of the user.
> Workflow: [workflow.prompt]
> Execute the task completely and autonomously. Do not ask clarifying questions.
> Report back what you did and the outcome."

This framing is a first-class variable in `InvestmentManagerPromptVars` so the agent always
understands whether it is in conversational mode or autonomous workflow mode.

### Result Delivery

A `WorkflowNotifier` abstract interface with a single `notify(user_id, result)` method:

```python
class WorkflowNotifier(ABC):
    async def notify(self, user_id: str, result: WorkflowResult) -> None: ...
```

**v1 — Passive (MongoDBWorkflowNotifier):**
Results are stored in a new `workflow_results` MongoDB collection. The agent surfaces pending
results at the start of the user's next conversation (same pattern as existing reminders).

**Future — Active:**
Additional notifier implementations (push notification, email) can be added and composed
without changing any workflow runner logic.

### Components to Build

| Component | Description |
|-----------|-------------|
| `models/agent_workflow.py` | `AgentWorkflow` and `WorkflowResult` Pydantic models |
| `services/agent_workflow.py` | MongoDB CRUD service for workflows |
| `services/workflow_result.py` | MongoDB service for workflow results |
| `services/workflow_notifier.py` | `WorkflowNotifier` ABC + `MongoDBWorkflowNotifier` |
| `services/workflow_runner.py` | Loads due workflows, runs agent, calls notifier |
| New tools in `tools.py` | create/get/update/delete workflow tools + `getWorkflowResults(user_id)` |
| `apps/rest_api/agent_workflows.py` | CRUD endpoints + `POST /workflows/check-and-run` + `GET /workflow_results/{user_id}` |

