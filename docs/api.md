# InvestPal API Reference

Welcome to the InvestPal API reference. This document provides detailed information about the available endpoints, request/response models, and example usage.

**Base URL**: `http://localhost:8000` (default for development)

---

## Chat Service

### Post Message
`POST /chat`

Send a message to the AI investment advisor for a specific session.

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
  "session_id": "string (optional)"
}
```
*If `session_id` is not provided, a new one will be generated.*

#### Response Body
```json
{
  "session_id": "string",
  "user_id": "string",
  "messages": []
}
```

#### Errors
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
  "messages": [
    {
      "role": "user | agent",
      "content": "string"
    }
  ]
}
```

#### Errors
- `404 Not Found`: Session not found.
- `500 Internal Server Error`: An error occurred during retrieval.

---

## User Context Service

### Create User Context
`POST /user_context`

Create initial context and portfolio for a user.

#### Request Body
```json
{
  "user_id": "string",
  "user_profile": {
    "key": "value"
  },
  "user_portfolio": [
    {
      "asset_class": "string",
      "symbol": "string",
      "name": "string",
      "quantity": 0.0
    }
  ]
}
```

#### Response Body
Same as request body.

#### Errors
- `409 Conflict`: User context already exists.
- `500 Internal Server Error`: An error occurred during creation.

### Get User Context
`GET /user_context/{user_id}`

Retrieve the context and portfolio for a specific user.

#### Parameters
- `user_id` (path): The unique identifier of the user.

#### Response Body
```json
{
  "user_id": "string",
  "user_profile": { ... },
  "user_portfolio": [ ... ]
}
```

#### Errors
- `404 Not Found`: User context not found.
- `500 Internal Server Error`: An error occurred during retrieval.

### Update User Context
`PUT /user_context`

Update existing context or portfolio for a user.

#### Request Body
Same as `POST /user_context`.

#### Response Body
Same as `POST /user_context`.

#### Errors
- `404 Not Found`: User context not found.
- `500 Internal Server Error`: An error occurred during update.
