# InvestPal API Reference

Welcome to the InvestPal API reference. This document provides detailed information about the available endpoints, request/response models, and example usage.

**Base URL**: `http://localhost:8000` (default for development)

---

## Chat Service

### Post Message
`POST /chat`

Send a message to the AI investment advisor for a specific session.

#### Headers (Optional)
- `X-Alpaca-Api-Key`: Alpaca API Key ID (required for Alpaca-related tools).
- `X-Alpaca-Api-Secret`: Alpaca API Secret Key (required for Alpaca-related tools).
- `X-Coinbase-Api-Key`: Coinbase API Key (required for Coinbase-related tools).
- `X-Coinbase-Api-Secret`: Coinbase API Secret (required for Coinbase-related tools). **Must be the base64-encoded version of the raw secret key.**

#### Request Body
```json
{
  "session_id": "string",
  "message": "string"
}
```

#### Response Body
```json
{
  "response": "string"
}
```

#### Errors
- `404 Not Found`: Session not found.
- `500 Internal Server Error`: An error occurred during response generation.

---

## Session Service

### Create Session
`POST /session`

Create a new chat session for a user.

#### Request Body
```json
{
  "user_id": "string",
  "session_id": "string (optional)",
  "name": "string (optional)"
}
```
*If `session_id` is not provided, a new one will be generated.*
*If `name` is not provided, it will default to the `session_id`. Its purpose is to provide a more human-readable name for the session.*

#### Response Body
```json
{
  "session_id": "string",
  "user_id": "string",
  "name": "string",
  "created_at": "string",
  "messages": []
}
```

#### Errors
- `400 Bad Request`: User context not found.
- `409 Conflict`: Session already exists.
- `500 Internal Server Error`: An error occurred during session creation.

### Get Session
`GET /session/{session_id}`

Retrieve the details and message history of a specific session.

#### Parameters
- `session_id` (path): The unique identifier of the session.

#### Response Body
```json
{
  "session_id": "string",
  "user_id": "string",
  "name": "string",
  "created_at": "string",
  "messages": [
    {
      "role": "user | agent",
      "content": "string",
      "created_at": "string"
    }
  ]
}
```

#### Errors
- `404 Not Found`: Session not found.
- `500 Internal Server Error`: An error occurred during retrieval.

---

### List User Sessions
`GET /sessions/{user_id}`

Retrieve a list of all sessions for a specific user, excluding the message history.

#### Parameters
- `user_id` (path): The unique identifier of the user.

#### Response Body
```json
[
  {
    "session_id": "string",
    "user_id": "string",
    "name": "string",
    "created_at": "string"
  }
]
```

#### Errors
- `500 Internal Server Error`: An error occurred during retrieval.

---

## User Context Service

### Create User Context
`POST /user_context`

Create initial context for a user.

#### Request Body
```json
{
  "user_id": "string",
  "user_profile": {
    "key": "value"
  } // (optional)
}
```

#### Response Body
```json
{
  "user_id": "string",
  "user_profile": { ... },
  "created_at": "string",
  "updated_at": "string"
}
```

#### Errors
- `409 Conflict`: User context already exists.
- `500 Internal Server Error`: An error occurred during creation.

### Get User Context
`GET /user_context/{user_id}`

Retrieve the context for a specific user.

#### Parameters
- `user_id` (path): The unique identifier of the user.

#### Response Body
```json
{
  "user_id": "string",
  "user_profile": { ... },
  "created_at": "string",
  "updated_at": "string"
}
```

#### Errors
- `404 Not Found`: User context not found.
- `500 Internal Server Error`: An error occurred during retrieval.

### Update User Context
`PUT /user_context`

Update existing context for a user.

#### Request Body
Same as `POST /user_context`.

#### Response Body
Same as `POST /user_context`.

#### Errors
- `404 Not Found`: User context not found.
- `500 Internal Server Error`: An error occurred during update.
