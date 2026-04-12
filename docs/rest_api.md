# InvestPal REST API Reference

Welcome to the InvestPal REST API reference. This document covers the HTTP endpoints exposed by the REST API server. For the MCP server tools, see [mcp_api.md](mcp_api.md).

**Base URL**: `http://localhost:8000` (default for development)

> **Interactive docs**: The REST API is built with FastAPI, so you get an auto-generated interactive UI at `http://localhost:8000/docs` and a raw OpenAPI schema at `http://localhost:8000/openapi.json`.

---

## Overview

The InvestPal REST API is the primary integration point for client applications. It exposes four services:

| Service | Purpose |
|---|---|
| **User Context** | Register users and store profile information before starting conversations |
| **Session** | Create and retrieve conversation sessions |
| **Chat** | Send messages to the AI investment advisor and receive responses |
| **Agent Reminders** | Retrieve reminders created by the agent for a user |

### Typical integration flow

```
1. POST /user_context        → Register the user
2. POST /session             → Open a conversation session
3. POST /chat (repeating)    → Exchange messages with the advisor
4. GET  /session/{id}        → Retrieve full conversation history
5. GET  /agent_reminders/{user_id} → Retrieve reminders set by the agent
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

## User Context Service

User context stores profile information about a user. A user context **must be created before any session can be opened** for that user.

### Create User Context

`POST /user_context`

Register a new user and optionally store their profile data.

**Request Body**

| Field | Type | Required | Description |
|---|---|---|---|
| `user_id` | string | yes | Your unique identifier for this user |
| `user_profile` | object | no | Arbitrary key-value profile data (age, risk tolerance, etc.) |

```json
{
  "user_id": "user-abc123",
  "user_profile": {
    "name": "Jane Smith",
    "age": 35,
    "risk_tolerance": "moderate"
  }
}
```

**Response** `201 Created`

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

**Errors**

| Status | Condition |
|---|---|
| `409 Conflict` | A user context for this `user_id` already exists |
| `500 Internal Server Error` | Unexpected server error |

---

### Get User Context

`GET /user_context/{user_id}`

Retrieve the stored context for a user.

**Path Parameters**

| Parameter | Type | Description |
|---|---|---|
| `user_id` | string | The unique identifier of the user |

**Response** `200 OK`

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

**Errors**

| Status | Condition |
|---|---|
| `404 Not Found` | No user context exists for the given `user_id` |
| `500 Internal Server Error` | Unexpected server error |

---

### Update User Context

`PUT /user_context`

Replace the profile data for an existing user. The entire `user_profile` object is overwritten — include all fields you want to keep.

**Request Body**

Same shape as `POST /user_context`. Both fields are required.

```json
{
  "user_id": "user-abc123",
  "user_profile": {
    "name": "Jane Smith",
    "age": 36,
    "risk_tolerance": "aggressive"
  }
}
```

**Response** `200 OK`

Same shape as `GET /user_context/{user_id}`.

**Errors**

| Status | Condition |
|---|---|
| `404 Not Found` | No user context exists for the given `user_id` |
| `500 Internal Server Error` | Unexpected server error |

---

## Session Service

Sessions represent individual conversation threads between a user and the AI advisor. Each session has its own isolated message history.

### Create Session

`POST /session`

Open a new conversation session for a user.

> **Note**: The user context for the given `user_id` must exist before creating a session.

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
| `400 Bad Request` | User context not found for the given `user_id` |
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

`GET /agent_reminders/{user_id}`

Retrieve all reminders for a user.

**Path Parameters**

| Parameter | Type | Description |
|---|---|---|
| `user_id` | string | The unique identifier of the user |

**Response** `200 OK`

```json
[
  {
    "user_id": "user-abc123",
    "reminder_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "reminder_description": "Review the Q1 earnings report for AAPL before next session",
    "created_at": "2024-01-15T10:40:00.000Z",
    "due_date": "2024-01-22"
  },
  {
    "user_id": "user-abc123",
    "reminder_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "reminder_description": "Check crypto allocation after BTC halving",
    "created_at": "2024-01-15T11:00:00.000Z",
    "due_date": null
  }
]
```

Returns an empty array `[]` if the user has no reminders.

The `due_date` field is in `YYYY-MM-DD` format and may be `null` if no due date was set.

**Errors**

| Status | Condition |
|---|---|
| `500 Internal Server Error` | Unexpected server error |

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
