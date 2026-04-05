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
| **User Context** | `updateUserContext`, `getUserContext` |
| **Conversation Memory** | `getUserConversationNotes`, `updateUserConversationNotes` |
| **Reminders** | `createAgentReminder`, `getAgentReminders`, `updateAgentReminder`, `deleteAgentReminder` |
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
        name="getUserContext",
        arguments={"user_id": "user-abc123"},
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
  "user_id": "user-abc123",
  "reminder_id": "rem-550e8400",
  "reminder_description": "Review Q1 earnings report for AAPL",
  "created_at": "2024-01-15T10:30:00.000Z",
  "due_date": "2024-01-31"
}
```

| Field | Type | Description |
|---|---|---|
| `user_id` | string | The user this reminder belongs to |
| `reminder_id` | string | Unique identifier for the reminder |
| `reminder_description` | string | Human-readable description |
| `created_at` | string | ISO 8601 UTC timestamp of creation |
| `due_date` | string \| null | Due date in `YYYY-MM-DD` format, or `null` if not set |

### Conversation Notes Object

Returned by `getUserConversationNotes`.

```json
{
  "user_id": "user-abc123",
  "date": "2024-01-15",
  "notes": {
    "discussed_stocks": "AAPL, MSFT",
    "user_concern": "volatility in tech sector",
    "action_item": "send rebalancing summary next session"
  }
}
```

| Field | Type | Description |
|---|---|---|
| `user_id` | string | The user these notes belong to |
| `date` | string | Date the conversation took place (`YYYY-MM-DD`) |
| `notes` | object | Free-form key-value pairs of notes |

### User Context Object

Returned by `getUserContext` and `updateUserContext`.

```json
{
  "user_id": "user-abc123",
  "user_profile": {
    "name": "Jane Smith",
    "age": 35,
    "risk_tolerance": "moderate"
  },
  "created_at": "2024-01-15T10:30:00.000Z",
  "updated_at": "2024-01-15T10:30:00.000Z"
}
```

---

## User Context Tools

### `updateUserContext`

Replace the user's profile. The provided `user_profile` **completely replaces** the existing one — include all fields you want to keep.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `user_id` | string | yes | The ID of the user to update |
| `user_profile` | object | yes | The complete new user profile (replaces existing) |

**Example call**

```python
result = await client.call_tool(
    name="updateUserContext",
    arguments={
        "user_id": "user-abc123",
        "user_profile": {
            "name": "Jane Smith",
            "age": 36,
            "risk_tolerance": "aggressive",
            "investment_goals": ["retirement", "real_estate"]
        },
    },
)
```

**Returns**: A [User Context Object](#user-context-object).

---

### `getUserContext`

Retrieve the stored context and profile for a user.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `user_id` | string | yes | The ID of the user to fetch context for |

**Example call**

```python
result = await client.call_tool(
    name="getUserContext",
    arguments={"user_id": "user-abc123"},
)
print(result.structured_content)
```

**Returns**: A [User Context Object](#user-context-object).

---

## Conversation Memory Tools

These tools give the agent the ability to persist and recall key details from past conversations, acting as a long-term memory layer.

### `getUserConversationNotes`

Retrieve conversation notes for a user, optionally filtered to a specific date. Use this to recall what was discussed in past sessions.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `user_id` | string | yes | The ID of the user |
| `date` | string | no | Filter by date in `YYYY-MM-DD` format. If omitted, notes for all dates are returned |

**Example call — all notes**

```python
result = await client.call_tool(
    name="getUserConversationNotes",
    arguments={"user_id": "user-abc123"},
)
```

**Example call — notes for a specific date**

```python
result = await client.call_tool(
    name="getUserConversationNotes",
    arguments={
        "user_id": "user-abc123",
        "date": "2024-01-15",
    },
)
```

**Returns**: A list of [Conversation Notes Objects](#conversation-notes-object). Returns an empty list if no notes exist.

---

### `updateUserConversationNotes`

Store or update conversation notes for a user on a given date. Notes are **merged** with any existing notes for that date — only the keys you provide are added or overwritten; other existing keys are preserved.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `user_id` | string | yes | The ID of the user |
| `date` | string | yes | The conversation date in `YYYY-MM-DD` format |
| `notes` | object | yes | Key-value pairs to merge into the notes for this date |

> **Tip**: Keep note values short and concise — they are loaded into the agent's context on every conversation.

**Example call**

```python
await client.call_tool(
    name="updateUserConversationNotes",
    arguments={
        "user_id": "user-abc123",
        "date": "2024-01-15",
        "notes": {
            "discussed_stocks": "AAPL, TSLA",
            "user_concern": "inflation impact on growth stocks",
            "follow_up": "check TSLA earnings next week",
        },
    },
)
```

**Returns**: `null` (no body). The operation is idempotent — calling it again with the same keys will overwrite those keys.

---

## Reminder Tools

Reminders allow the agent to create and manage time-sensitive action items on behalf of the user. They persist across sessions and are surfaced to the agent at the start of each conversation.

### `createAgentReminder`

Create a new reminder for a user.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `user_id` | string | yes | The ID of the user this reminder is for |
| `reminder_description` | string | yes | A clear description of what to be reminded about |
| `due_date` | string | no | Optional due date in `YYYY-MM-DD` format |

**Example call**

```python
result = await client.call_tool(
    name="createAgentReminder",
    arguments={
        "user_id": "user-abc123",
        "reminder_description": "Review AAPL earnings report and update portfolio allocation",
        "due_date": "2024-01-31",
    },
)
```

**Returns**: The created [Reminder Object](#reminder-object).

```json
{
  "user_id": "user-abc123",
  "reminder_id": "rem-550e8400",
  "reminder_description": "Review AAPL earnings report and update portfolio allocation",
  "created_at": "2024-01-15T10:30:00.000Z",
  "due_date": "2024-01-31"
}
```

---

### `getAgentReminders`

Retrieve all reminders for a user.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `user_id` | string | yes | The ID of the user |

**Example call**

```python
result = await client.call_tool(
    name="getAgentReminders",
    arguments={"user_id": "user-abc123"},
)
```

**Returns**: A list of [Reminder Objects](#reminder-object). Returns an empty list if no reminders exist.

```json
[
  {
    "user_id": "user-abc123",
    "reminder_id": "rem-550e8400",
    "reminder_description": "Review AAPL earnings report",
    "created_at": "2024-01-15T10:30:00.000Z",
    "due_date": "2024-01-31"
  },
  {
    "user_id": "user-abc123",
    "reminder_id": "rem-661f9511",
    "reminder_description": "Rebalance crypto allocation",
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
| `user_id` | string | yes | The ID of the user the reminder belongs to |
| `reminder_id` | string | yes | The unique ID of the reminder to update |
| `reminder_description` | string | no | New description. If omitted, the existing description is kept |
| `due_date` | string | no | New due date in `YYYY-MM-DD` format. If omitted, the existing due date is kept |

**Example call — update due date only**

```python
result = await client.call_tool(
    name="updateAgentReminder",
    arguments={
        "user_id": "user-abc123",
        "reminder_id": "rem-550e8400",
        "due_date": "2024-02-15",
    },
)
```

**Example call — update both fields**

```python
result = await client.call_tool(
    name="updateAgentReminder",
    arguments={
        "user_id": "user-abc123",
        "reminder_id": "rem-550e8400",
        "reminder_description": "Review AAPL and MSFT earnings, update allocation",
        "due_date": "2024-02-15",
    },
)
```

**Returns**: The updated [Reminder Object](#reminder-object), or `null` if the reminder was not found.

---

### `deleteAgentReminder`

Permanently delete a reminder.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `user_id` | string | yes | The ID of the user the reminder belongs to |
| `reminder_id` | string | yes | The unique ID of the reminder to delete |

**Example call**

```python
await client.call_tool(
    name="deleteAgentReminder",
    arguments={
        "user_id": "user-abc123",
        "reminder_id": "rem-550e8400",
    },
)
```

**Returns**: `null` (no body). The operation succeeds silently even if the `reminder_id` does not exist.

---

## Prompts

### `get_invstment_advisor_prompt`

Returns the system prompt used to configure the InvestPal investment advisor agent for a given user. This prompt is pre-loaded with the user's context and instructs the agent on how to behave.

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
| User not found | The `user_id` does not exist in the database. Ensure the user context was created via the REST API first (`POST /user_context`) |
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
