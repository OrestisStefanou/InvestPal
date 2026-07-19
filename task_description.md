# Task Description
Migrate agent reminders storage from mongodb to turso db

We need a new agent_reminder table with the followig columns
- id -> Text(uuid)
- description -> Text
- due_date -> date
- created_at -> date
- deleted_at -> date


After we create the table we have to backfill it with any existing reminders that we have in mongo

---

# Implementation Plan

Migrate the agent reminders storage from MongoDB to Turso (local SQLite), following the same pattern as `user_profile_notes`. Drop `user_id` everywhere (single-user project). Switch delete to soft-delete via `deleted_at`. Remove user-context validation. After creating the table, backfill from existing MongoDB data.

## Proposed Changes

### 1. Database Schema

#### [MODIFY] schema.sql
Add the `agent_reminders` table:
```sql
CREATE TABLE IF NOT EXISTS agent_reminders (
    id TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    due_date TEXT,
    created_at TEXT NOT NULL,
    deleted_at TEXT
);
```

---

### 2. Repository Layer

#### [NEW] repos/agent_reminders.py
New Turso repository following the same pattern as `repos/user_profile_notes.py`:
- `AgentReminderRow` dataclass (id, description, due_date, created_at, deleted_at)
- `AgentRemindersTable` class with methods:
  - `create_reminder(description, due_date) -> AgentReminderRow`
  - `get_reminders() -> list[AgentReminderRow]` — filters out soft-deleted rows (`WHERE deleted_at IS NULL`)
  - `delete_reminder(reminder_id) -> bool` — soft-delete (sets `deleted_at` to current timestamp)
  - `update_reminder(reminder_id, description, due_date) -> AgentReminderRow | None`
  - `insert_row(row: AgentReminderRow)` — for backfill, inserts a fully-formed row (INSERT OR IGNORE)

---

### 3. Model

#### [MODIFY] models/agent_reminder.py
- Remove `user_id` field from `AgentReminder`
- Rename `reminder_id` -> `id`, `reminder_description` -> `description` to match the new schema

---

### 4. Service Layer

#### [MODIFY] services/agent_reminder.py
- Remove `user_id` from the `AgentReminderService` ABC method signatures (create, get, delete, update)
- Add a new `TursoAgentReminderService` class implementing `AgentReminderService`
  - Uses `AgentRemindersTable` from the new repo, wrapped in `asyncio.to_thread()` (same as `UserProfileService`)
  - No user-context existence checks
- Remove `MongoDBAgentReminderService`

---

### 5. Dependency Injection (FastAPI REST API)

#### [MODIFY] dependencies.py
- Change `get_agent_reminder_service()` to return `TursoAgentReminderService` instead of `MongoDBAgentReminderService`
- Remove the MongoDB client dependency from this function
- Import and instantiate `AgentRemindersTable`

---

### 6. MCP API

#### [MODIFY] apps/mcp_api/app.py
- Change `get_agent_reminder_service()` to return `TursoAgentReminderService` instead of `MongoDBAgentReminderService`
- Remove the MongoDB context dependency from this function
- Remove `user_id` parameter from all reminder MCP tool functions (`createAgentReminder`, `getAgentReminders`, `updateAgentReminder`, `deleteAgentReminder`)

---

### 7. REST API Routes

#### [MODIFY] apps/rest_api/agent_reminders.py
- Remove `user_id` from the route path and `AgentReminderSchema`
- Change the endpoint from `/agent_reminders/{user_id}` to `/agent_reminders`
- Remove `UserContextNotFoundError` handling

---

### 8. Agent Tools (LangChain)

#### [MODIFY] services/agents/tools.py
- Remove `user_id` from `CreateAgentReminderToolInput`, `UpdateAgentReminderToolInput`, `DeleteAgentReminderToolInput`
- Remove `user_id` parameter from `create_agent_reminder`, `get_agent_reminders`, `update_agent_reminder`, `delete_agent_reminder` tool functions
- Remove `user_id` from the service method calls

---

### ~~9. Backfill Script~~ (deferred)

---

### Files NOT changed (no reminder-related modifications needed)
- `services/agent_service.py` — only passes `agent_reminder_service` through to runtime context, no `user_id` coupling
- `services/agent_workflows/runner.py` — only stores `agent_reminder_service`, doesn't call reminder methods directly
- `main.py` — no changes needed

## Verification Plan
### Manual Verification
- Start the app and confirm reminder CRUD operations work through the MCP and REST APIs
- Verify soft-deleted reminders don't appear in get results
