# InvestPal REST API Reference

Welcome to the InvestPal REST API reference. This document covers the HTTP endpoints exposed by the REST API server. For the MCP server tools, see [mcp_api.md](mcp_api.md).

**Base URL**: `http://localhost:8000` (default for development)

> **Interactive docs**: The REST API is built with FastAPI, so you get an auto-generated interactive UI at `http://localhost:8000/docs` and a raw OpenAPI schema at `http://localhost:8000/openapi.json`.

---

## Overview

The InvestPal REST API is the primary integration point for client applications. It exposes these services:

| Service | Purpose |
|---|---|
| **Session** | Create and retrieve conversation sessions |
| **Chat** | Send messages to the AI investment advisor and receive responses |
| **Agent Reminders** | Retrieve reminders created by the agent |
| **Agent Workflows** | Manage scheduled, autonomous workflows and retrieve their execution results |

### Typical integration flow

```
1. POST /session             → Open a conversation session
2. POST /chat (repeating)    → Exchange messages with the advisor
3. GET  /session/{id}        → Retrieve full conversation history
4. GET  /agent_reminders     → Retrieve reminders set by the agent
```

---

## Authentication & Headers

Most endpoints require no authentication headers. The following **optional** headers are forwarded to the relevant brokerage integrations when provided:

| Header | Required for |
|---|---|
| `X-Alpaca-Api-Key` | Alpaca-related tools (portfolio data, trading) |
| `X-Alpaca-Api-Secret` | Alpaca-related tools |
| `X-Coinbase-Api-Key` | Coinbase-related tools |
| `X-Coinbase-Api-Secret` | Coinbase-related tools — **must be the base64-encoded version of the raw secret key** |

These headers are only needed on the `POST /chat` endpoint when the user's query requires accessing brokerage data.

---

## Session Service

Sessions represent individual conversation threads between a user and the AI advisor. Each session has its own isolated message history.

### Create Session

`POST /session`

Open a new conversation session for a user.

**Request Body**

| Field | Type | Required | Description |
|---|---|---|---|
| `user_id` | string | yes | The ID of the user who owns this session |
| `session_id` | string | no | Custom session ID. A UUID is generated if omitted |
| `name` | string | no | Human-readable session name. Defaults to `session_id` if omitted |

```json
{
  "user_id": "user-abc123",
  "name": "Q1 Portfolio Review"
}
```

**Response** `201 Created`

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-abc123",
  "name": "Q1 Portfolio Review",
  "created_at": "2024-01-15T10:35:00.000Z",
  "messages": []
}
```

**Errors**

| Status | Condition |
|---|---|
| `409 Conflict` | A session with the provided `session_id` already exists |
| `500 Internal Server Error` | Unexpected server error |

---

### Get Session

`GET /session/{session_id}`

Retrieve the full message history of a session.

**Path Parameters**

| Parameter | Type | Description |
|---|---|---|
| `session_id` | string | The unique identifier of the session |

**Response** `200 OK`

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-abc123",
  "name": "Q1 Portfolio Review",
  "created_at": "2024-01-15T10:35:00.000Z",
  "messages": [
    {
      "role": "user",
      "content": "What is my portfolio performance this quarter?",
      "created_at": "2024-01-15T10:36:00.000Z"
    },
    {
      "role": "agent",
      "content": "Based on your current holdings...",
      "created_at": "2024-01-15T10:36:05.000Z"
    }
  ]
}
```

The `role` field is either `"user"` or `"agent"`.

**Errors**

| Status | Condition |
|---|---|
| `404 Not Found` | No session with the given `session_id` exists |
| `500 Internal Server Error` | Unexpected server error |

---

### List User Sessions

`GET /sessions/{user_id}`

Return all sessions for a user, without message history.

**Path Parameters**

| Parameter | Type | Description |
|---|---|---|
| `user_id` | string | The unique identifier of the user |

**Response** `200 OK`

```json
[
  {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "user-abc123",
    "name": "Q1 Portfolio Review",
    "created_at": "2024-01-15T10:35:00.000Z"
  },
  {
    "session_id": "661f9511-f30c-52e5-b827-557766551111",
    "user_id": "user-abc123",
    "name": "Crypto Strategy",
    "created_at": "2024-01-16T09:00:00.000Z"
  }
]
```

Returns an empty array `[]` if the user has no sessions.

**Errors**

| Status | Condition |
|---|---|
| `500 Internal Server Error` | Unexpected server error |

---

## Chat Service

### Post Message

`POST /chat`

Send a user message to the AI investment advisor and receive a response. The message is appended to the session's history, and the agent's reply is returned synchronously.

**Optional Headers** — include only when the user's query requires brokerage access:

```
X-Alpaca-Api-Key: <alpaca-key-id>
X-Alpaca-Api-Secret: <alpaca-secret-key>
X-Coinbase-Api-Key: <coinbase-key>
X-Coinbase-Api-Secret: <base64-encoded-coinbase-secret>
```

**Request Body**

| Field | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | yes | The session to send the message to |
| `message` | string | yes | The user's message text |

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Should I rebalance my portfolio this month?"
}
```

**Response** `200 OK`

```json
{
  "response": "Based on your current allocation and recent market movements, here is my analysis..."
}
```

**Errors**

| Status | Condition |
|---|---|
| `404 Not Found` | No session with the given `session_id` exists |
| `500 Internal Server Error` | An error occurred during response generation |

---

## Agent Reminders Service

Agent reminders are notes or follow-up actions the AI advisor creates on behalf of the user during a conversation.

### Get Agent Reminders

`GET /agent_reminders`

Retrieve all reminders.

**Response** `200 OK`

```json
[
  {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "description": "Review the Q1 earnings report for AAPL before next session",
    "created_at": "2024-01-15T10:40:00.000Z",
    "due_date": "2024-01-22"
  },
  {
    "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "description": "Check crypto allocation after BTC halving",
    "created_at": "2024-01-15T11:00:00.000Z",
    "due_date": null
  }
]
```

Returns an empty array `[]` if there are no reminders. Deleted reminders are soft-deleted and never appear in the response.

The `due_date` field is in `YYYY-MM-DD` format and may be `null` if no due date was set.

**Errors**

| Status | Condition |
|---|---|
| `500 Internal Server Error` | Unexpected server error |

---

## Agent Workflows Service

Scheduled agent workflows allow the AI to autonomously execute instructions on a predefined schedule.

### Create Workflow

`POST /workflows`

Create a new scheduled workflow.

**Request Body**

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | A human-readable name for the workflow |
| `description` | string | yes | Goal-only description of what the agent should achieve on each run |
| `schedule` | string | yes | Cron expression (e.g. `0 0 * * 5` for every Friday) |

**Response** `201 Created`

```json
{
  "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Weekly Portfolio Review",
  "description": "Review my portfolio and summarise it",
  "schedule": "0 0 * * 5",
  "status": "active",
  "created_at": "2024-01-15T10:35:00.000Z",
  "last_run_at": null,
  "next_run_at": "2024-01-19T00:00:00.000Z"
}
```

---

### Get Workflows

`GET /workflows`

Retrieve all workflows.

---

### Update Workflow

`PATCH /workflows/{workflow_id}`

Update the fields of a workflow. Only the fields provided are changed. Passing a new `schedule` re-bases `next_run_at` from now.

---

### Delete Workflow

`DELETE /workflows/{workflow_id}`

Delete a workflow. Results of its past runs are kept.

---

### Check and Run Workflows

`POST /workflows/check-and-run`

Heartbeat endpoint to check for and execute due workflows. Intended to be called by an external cron job.

Each run is claimed atomically: the workflow flips to `running` so a concurrent heartbeat cannot pick it up. Storing the run's result is what completes the run — it records `last_run_at`, advances `next_run_at` from the cron expression and returns the status to `active`, all in one transaction. A run that fails before storing a result keeps its `next_run_at`, so it is retried on a later heartbeat.

---

### Get Workflow Results

`GET /workflow_results`

Retrieve the results of executed workflows, most recent first.

**Query Parameters**

| Name | Type | Description |
|---|---|---|
| `limit` | integer | Maximum number of results to return. Defaults to `10` |

---

## Data Types

### Timestamps

All `created_at` and `updated_at` fields are ISO 8601 strings in UTC, e.g. `"2024-01-15T10:30:00.000Z"`.

### User Profile

The `user_profile` field is a free-form JSON object. There is no enforced schema — store whatever attributes are relevant to your application (e.g. name, age, risk tolerance, investment goals).

```json
{
  "name": "Jane Smith",
  "age": 35,
  "risk_tolerance": "moderate",
  "investment_goals": ["retirement", "home_purchase"],
  "preferred_sectors": ["tech", "healthcare"]
}
```
