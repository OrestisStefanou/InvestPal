# InvestPal MCP API Reference

Welcome to the InvestPal MCP (Model Context Protocol) API reference. This document describes the tools and prompts exposed by the InvestPal MCP server, which enables AI agents and MCP-compatible clients to interact with user data, conversation memory, and reminders.

For the standard HTTP REST API, see [rest_api.md](rest_api.md).

**Default MCP endpoint**: `http://localhost:9000/mcp`

---

## Overview

The InvestPal MCP server is built with [FastMCP](https://github.com/jlowin/fastmcp) and exposes tools over the **Streamable HTTP** transport. Any MCP-compatible client can connect to it and call the tools described below.

The server exposes two categories of tools and one prompt:

| Category | Tools |
|---|---|
| **User Profile** | `getUserProfileNotes`, `createUserProfileNote`, `markUserProfileNoteAsOutdated` |
| **Conversation Memory** | `getUserConversationNotes`, `createUserConversationNote` |
| **Reminders** | `createAgentReminder`, `getAgentReminders`, `updateAgentReminder`, `deleteAgentReminder` |
| **Agent Workflows** | `createAgentWorkflow`, `getAgentWorkflows`, `updateAgentWorkflow`, `deleteAgentWorkflow`, `getWorkflowResults`, `storeWorkflowResult` |
| **Prompts** | `get_invstment_advisor_prompt` |

---

## Connecting to the MCP Server

### Using FastMCP Client (Python)

```python
from fastmcp import Client

client = Client("http://127.0.0.1:9000/mcp")

async with client:
    await client.ping()  # verify connection

    result = await client.call_tool(
        name="getUserProfileNotes",
        arguments={},
    )
    print(result.structured_content)
```

### Using any MCP-compatible client

Configure your client to connect via Streamable HTTP transport to `http://<host>:9000/mcp`. No authentication headers are required by the MCP server itself.

---

## Common Data Types

### Reminder Object

Returned by reminder tools.

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "description": "Review Q1 earnings report for AAPL",
  "created_at": "2024-01-15T10:30:00.000Z",
  "due_date": "2024-01-31"
}
```

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique identifier for the reminder (UUID) |
| `description` | string | Human-readable description |
| `created_at` | string | ISO 8601 timestamp of creation |
| `due_date` | string \| null | Due date in `YYYY-MM-DD` format, or `null` if not set |

### Conversation Note Object

Returned by `getUserConversationNotes` and `createUserConversationNote`.

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "date": "2024-01-15",
  "note": "Concerned about volatility in the tech sector",
  "created_at": "2024-01-15T10:30:00.000Z"
}
```

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique identifier for the note (UUID) |
| `date` | string | Date the conversation took place (`YYYY-MM-DD`) |
| `note` | string | The note text |
| `created_at` | string | ISO 8601 timestamp of creation |

A date can hold any number of notes.

### Workflow Object

Returned by the workflow tools.

```json
{
  "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Weekly portfolio review",
  "description": "Review the portfolio and report anything notable",
  "schedule": "0 0 * * 5",
  "status": "active",
  "created_at": "2024-01-15T10:35:00.000Z",
  "last_run_at": null,
  "next_run_at": "2024-01-19T00:00:00.000Z"
}
```

| Field | Type | Description |
|---|---|---|
| `workflow_id` | string | Unique identifier (UUID) |
| `name` | string | Human-readable name |
| `description` | string | What the agent should achieve on each run |
| `schedule` | string | Cron expression |
| `status` | string | `active`, `paused`, or `running` while a run is in flight |
| `created_at` | string | ISO 8601 timestamp of creation |
| `last_run_at` | string \| null | ISO 8601 timestamp of the last completed run |
| `next_run_at` | string \| null | ISO 8601 timestamp of the next scheduled run |

### Workflow Result Object

Returned by `getWorkflowResults` and `storeWorkflowResult`.

```json
{
  "result_id": "550e8400-e29b-41d4-a716-446655440000",
  "workflow_id": "661f9511-f3ac-52e5-b827-557766551111",
  "workflow_name": "Weekly portfolio review",
  "output": "Portfolio is up 2.1% this week, no action needed",
  "ran_at": "2024-01-19T00:00:12.000Z"
}
```

| Field | Type | Description |
|---|---|---|
| `result_id` | string | Unique identifier (UUID) |
| `workflow_id` | string | The workflow that produced this result |
| `workflow_name` | string | The workflow's name at execution time |
| `output` | string | The agent's report for this run |
| `ran_at` | string | ISO 8601 timestamp of the run |

Results outlive the workflow that produced them.

### Profile Note Object

Returned by `getUserProfileNotes` and `createUserProfileNote`.

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "note": "Moderate risk tolerance, 10 year horizon",
  "created_at": "2024-01-15T10:30:00.000Z"
}
```

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique identifier for the note (UUID) |
| `note` | string | One self-contained fact about the user |
| `created_at` | string | ISO 8601 timestamp of creation |

The profile is the set of notes that have not been marked outdated.

---

## User Profile Tools

The user's profile is stored as a set of notes rather than a single document. Each note is one
self-contained fact. The profile is injected into the investment advisor's system prompt on every
conversation, so notes should be short.

### `getUserProfileNotes`

Retrieve the notes that make up the profile. Notes marked as outdated are not returned.

**Parameters**

None.

**Example call**

```python
result = await client.call_tool(
    name="getUserProfileNotes",
    arguments={},
)
```

**Returns**: A list of [Profile Note Objects](#profile-note-object). Returns an empty list if nothing is recorded yet.

---

### `createUserProfileNote`

Store a permanent fact about the user. This adds a note; it never replaces the existing ones.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `note` | string | yes | One self-contained fact, e.g. risk tolerance, horizon, goals or sector interests |

**Example call**

```python
result = await client.call_tool(
    name="createUserProfileNote",
    arguments={"note": "Moderate risk tolerance, 10 year horizon"},
)
```

**Returns**: The created [Profile Note Object](#profile-note-object).

---

### `markUserProfileNoteAsOutdated`

Mark a note as outdated so it stops being part of the profile. Use this instead of editing when a fact stops being true.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `note_id` | string | yes | The id of the note to mark as outdated |

**Example call**

```python
await client.call_tool(
    name="markUserProfileNoteAsOutdated",
    arguments={"note_id": "550e8400-e29b-41d4-a716-446655440000"},
)
```

**Returns**: A confirmation string.

---

## Conversation Memory Tools

These tools give the agent the ability to persist and recall key details from past conversations, acting as a long-term memory layer.

### `getUserConversationNotes`

Retrieve conversation notes, ordered by most recent first. Use this to recall what was discussed in past sessions.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `limit` | integer \| null | no | Maximum number of notes to return, most recent first. Defaults to `5`. Pass `null` to return all notes |

**Example call — the 5 most recent notes**

```python
result = await client.call_tool(
    name="getUserConversationNotes",
    arguments={},
)
```

**Example call — every note on record**

```python
result = await client.call_tool(
    name="getUserConversationNotes",
    arguments={"limit": None},
)
```

**Returns**: A list of [Conversation Note Objects](#conversation-note-object), ordered by date descending and then by creation time descending. Returns an empty list if no notes exist.

---

### `createUserConversationNote`

Store a conversation note. A date can hold any number of notes, so this adds a note rather than replacing what is already stored.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `note` | string | yes | The note text |
| `date` | string \| null | no | The conversation date in `YYYY-MM-DD` format. Defaults to today. Rejected if provided and not `YYYY-MM-DD` |

> **Tip**: Keep notes short and concise — they are loaded into the agent's context on every conversation.

**Example call — today**

```python
await client.call_tool(
    name="createUserConversationNote",
    arguments={"note": "Concerned about the inflation impact on growth stocks"},
)
```

**Example call — a specific date**

```python
await client.call_tool(
    name="createUserConversationNote",
    arguments={
        "note": "Concerned about the inflation impact on growth stocks",
        "date": "2024-01-15",
    },
)
```

**Returns**: The created [Conversation Note Object](#conversation-note-object). This operation is not idempotent — calling it twice with the same text stores two separate notes.

---

## Reminder Tools

Reminders allow the agent to create and manage time-sensitive action items on behalf of the user. They persist across sessions and are surfaced to the agent at the start of each conversation.

### `createAgentReminder`

Create a new reminder.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `reminder_description` | string | yes | A clear description of what to be reminded about |
| `due_date` | string | no | Optional due date in `YYYY-MM-DD` format |

**Example call**

```python
result = await client.call_tool(
    name="createAgentReminder",
    arguments={
        "reminder_description": "Review AAPL earnings report and update portfolio allocation",
        "due_date": "2024-01-31",
    },
)
```

**Returns**: The created [Reminder Object](#reminder-object).

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "description": "Review AAPL earnings report and update portfolio allocation",
  "created_at": "2024-01-15T10:30:00.000Z",
  "due_date": "2024-01-31"
}
```

---

### `getAgentReminders`

Retrieve all reminders. Deleted reminders are never returned.

**Parameters**

None.

**Example call**

```python
result = await client.call_tool(
    name="getAgentReminders",
    arguments={},
)
```

**Returns**: A list of [Reminder Objects](#reminder-object). Returns an empty list if no reminders exist.

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "description": "Review AAPL earnings report",
    "created_at": "2024-01-15T10:30:00.000Z",
    "due_date": "2024-01-31"
  },
  {
    "id": "661f9511-f3ac-52e5-b827-557766551111",
    "description": "Rebalance crypto allocation",
    "created_at": "2024-01-16T09:00:00.000Z",
    "due_date": null
  }
]
```

---

### `updateAgentReminder`

Update the description or due date of an existing reminder. Only the fields you provide are changed; omitted fields retain their current values.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `reminder_id` | string | yes | The unique ID of the reminder to update |
| `reminder_description` | string | no | New description. If omitted, the existing description is kept |
| `due_date` | string | no | New due date in `YYYY-MM-DD` format. If omitted, the existing due date is kept |

**Example call — update due date only**

```python
result = await client.call_tool(
    name="updateAgentReminder",
    arguments={
        "reminder_id": "550e8400-e29b-41d4-a716-446655440000",
        "due_date": "2024-02-15",
    },
)
```

**Example call — update both fields**

```python
result = await client.call_tool(
    name="updateAgentReminder",
    arguments={
        "reminder_id": "550e8400-e29b-41d4-a716-446655440000",
        "reminder_description": "Review AAPL and MSFT earnings, update allocation",
        "due_date": "2024-02-15",
    },
)
```

**Returns**: The updated [Reminder Object](#reminder-object). Errors if no live reminder with that `reminder_id` exists.

---

### `deleteAgentReminder`

Delete a reminder. The row is soft-deleted: it is retained in storage with a `deleted_at` timestamp and is excluded from all subsequent reads.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `reminder_id` | string | yes | The unique ID of the reminder to delete |

**Example call**

```python
await client.call_tool(
    name="deleteAgentReminder",
    arguments={
        "reminder_id": "550e8400-e29b-41d4-a716-446655440000",
    },
)
```

**Returns**: `null` (no body). Errors if no live reminder with that `reminder_id` exists.

---

## Agent Workflow Tools

Agent Workflows enable the AI advisor to autonomously execute recurring tasks on behalf of the user using cron schedules.

### `createAgentWorkflow`

Create a new scheduled workflow. `next_run_at` is computed from the cron expression at creation.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | A short human-readable name |
| `description` | string | yes | Goal-only description of what to achieve on each run. No tool names, no user data, no implementation steps |
| `schedule` | string | yes | Cron expression, e.g. `0 0 1 * *` for monthly on the 1st |

**Returns**: A [Workflow Object](#workflow-object).

---

### `getAgentWorkflows`

Retrieve all scheduled workflows.

**Parameters**

None.

**Returns**: A list of [Workflow Objects](#workflow-object).

---

### `updateAgentWorkflow`

Update an existing workflow. Only the fields provided are changed. Passing a new `schedule` re-bases `next_run_at` from now.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `workflow_id` | string | yes | The workflow to update |
| `name` | string | no | New name |
| `description` | string | no | New goal-only description |
| `schedule` | string | no | New cron expression |
| `status` | string | no | `active` or `paused`. A paused workflow is never claimed for a run |

**Returns**: The updated [Workflow Object](#workflow-object).

---

### `deleteAgentWorkflow`

Delete a workflow. The results of its past runs are kept.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `workflow_id` | string | yes | The workflow to delete |

---

### `getWorkflowResults`

Get the results of past workflow runs, ordered by most recent first.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `limit` | integer \| null | no | Maximum number of results. Defaults to `10`. Pass `null` for all |

**Returns**: A list of [Workflow Result Objects](#workflow-result-object).

---

### `storeWorkflowResult`

Store the result of a workflow run. **This also completes the run**: in a single transaction it records the result, sets the workflow's `last_run_at`, advances `next_run_at` from the cron schedule and returns the status to `active`.

A result whose `workflow_id` no longer exists is still stored; there is simply no schedule to advance.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `workflow_id` | string | yes | The workflow this result belongs to |
| `workflow_name` | string | yes | The workflow's name at execution time |
| `output` | string | yes | The agent's report for this run |

**Returns**: The stored [Workflow Result Object](#workflow-result-object).

---

## Prompts

### `get_invstment_advisor_prompt`

Returns the system prompt used to configure the InvestPal investment advisor agent for a given user.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `user_id` | string | yes | The ID of the user to generate the prompt for |

**Example call**

```python
result = await client.get_prompt(
    name="get_invstment_advisor_prompt",
    arguments={"user_id": "user-abc123"},
)
print(result.messages[0].content.text)
```

**Returns**: The investment advisor system prompt string, personalized for the given `user_id`.

---

## Error Handling

The MCP server propagates errors as MCP tool error responses. In the FastMCP Python client, a failed tool call raises an exception. Common causes:

| Cause | Description |
|---|---|
| Invalid date format | Dates must be in `YYYY-MM-DD` format |
| Database unavailable | The MongoDB connection failed on startup |

---

## Running the MCP Server

```bash
python -m apps.mcp_api.app
# or directly:
python apps/mcp_api/app.py
```

The server starts on port `9000` by default and listens at `http://0.0.0.0:9000/mcp`.

Required environment variables (see `.env`):

| Variable | Description |
|---|---|
| `MONGO_URI` | MongoDB connection string |
| `MONGO_DB_NAME` | Database name |
