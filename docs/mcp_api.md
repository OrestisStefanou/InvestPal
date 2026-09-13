# InvestPal MCP API Reference

Welcome to the InvestPal MCP (Model Context Protocol) API reference. This document describes the tools and prompts exposed by the InvestPal MCP server, which enables AI agents and MCP-compatible clients to interact with user data, conversation memory, and reminders.

For the standard HTTP REST API, see [rest_api.md](rest_api.md).

**Default MCP endpoint**: `http://localhost:9000/mcp`

---

## Overview

The InvestPal MCP server is built with [FastMCP](https://github.com/jlowin/fastmcp) and exposes tools over the **Streamable HTTP** transport. Any MCP-compatible client can connect to it and call the tools described below.

The server exposes these categories of tools and one prompt:

| Category | Tools |
|---|---|
| **User Profile** | `getUserProfileNotes`, `createUserProfileNote`, `markUserProfileNoteAsOutdated` |
| **Holdings** | `getHoldings`, `upsertHolding`, `closeHolding` |
| **Ticker Records** | `getTickerRecords`, `upsertTickerRecord`, `deleteTickerRecord` |
| **Conversation Memory** | `getUserConversationNotes`, `searchUserConversationNotes`, `createUserConversationNote` |
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

### Conversation Note Search Result Object

Returned by `searchUserConversationNotes`. A [Conversation Note Object](#conversation-note-object) with one extra field.

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "date": "2024-01-15",
  "note": "Concerned about volatility in the tech sector",
  "created_at": "2024-01-15T10:30:00.000Z",
  "similarity": 0.8147
}
```

| Field | Type | Description |
|---|---|---|
| `similarity` | number | How closely the note matches the query in meaning, from `0.0` (unrelated) to `1.0` (identical meaning) |

Scores are relative, not absolute. Notes on the same broad topic typically land between `0.6` and `0.9`, so compare scores within a result set rather than against a fixed cutoff.

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

Store one durable fact about the client. This adds a note; it never replaces the existing ones.

The test the agent is given: would this still be true, and still matter, in six months
regardless of market prices? Age, risk tolerance, goals, horizon, knowledge level, profession,
income, expenses, liquidity constraints and sector preferences pass. Holdings, share counts,
prices, P&L, watchlist entries, entry triggers, research theses and session events do not:
they belong in `upsertHolding`, `upsertTickerRecord` and `createUserConversationNote`
respectively. The profile is injected into every session under a character budget, so content
stored here that belongs elsewhere crowds out the facts that matter.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `note` | string | yes | One self-contained durable fact, e.g. risk tolerance, horizon, goals or sector interests |

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

### `searchUserConversationNotes`

Search conversation notes by meaning rather than by date. Prefer this over `getUserConversationNotes` when looking for a specific topic; use `getUserConversationNotes` when you just want to review what happened most recently.

Matching is semantic, not keyword-based: a query for "retirement savings split" will surface a note about rebalancing a pension allocation even though the two share no words. Embeddings are generated locally (see [Semantic search](#semantic-search)), so note text never leaves the machine.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `query` | string | yes | A natural-language description of what to recall. Full sentences work better than keywords |
| `limit` | integer | no | Maximum number of notes to return, most similar first. Defaults to `5` |
| `min_similarity` | number \| null | no | Optional `0.0`-`1.0` similarity floor. Defaults to `null` (no filtering) |

**Example call**

```python
result = await client.call_tool(
    name="searchUserConversationNotes",
    arguments={"query": "the client's view on pension allocation", "limit": 3},
)
```

**Returns**: A list of [Conversation Note Search Result Objects](#conversation-note-search-result-object), most similar first. Returns an empty list if no notes exist, if none clear `min_similarity`, or if embeddings are disabled.

> **Note**: Notes are embedded when they are created. A note whose embedding failed, or one written before the embedding model was changed, will not appear in results until `make backfill_embeddings` has been run.

---

### `createUserConversationNote`

Store what happened in a session. This is the home for anything dated: decisions taken and
the reasoning behind them, analysis run and what it concluded, trades executed, advice given
and follow-ups left open. A date can hold any number of notes, so this adds a note rather
than replacing what is already stored.

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

## Holdings Tools

What the client owns, whatever the origin: broker positions, cash, fixed income and
off-platform assets. Every row carries a `source` and an `as_of`.

**The freshness contract.** A row whose `source` is a broker (`interactive_brokers`,
`coinbase`, `alpaca`) is a *cache* of that broker's own record. When the broker's tools
are reachable, call them and write the result back with `upsertHolding`; never prefer the
stored row over a live broker. When they are not, the stored row is the best record there
is, but every figure must be quoted with its `as_of` date rather than presented as current.
Rows with `source = "manual"` came from the client and nothing can contradict them.

Market prices, market values and P&L are never stored. Compute them from live quotes
against the stored quantities.

### `getHoldings`

Return the client's positions.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `include_closed` | boolean | no | Include closed positions. Defaults to `false` |

**Returns**: A list of Holding objects.

---

### `upsertHolding`

Record or refresh one position. Identified by `name` plus `custodian`, so writing the same
pair again updates that row rather than adding a second one. Only the fields passed are
written, so refreshing a share count leaves the cost basis alone.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | What the position is: `"NVDA"`, `"Bank cash"`. Part of the identity |
| `kind` | string \| null | on create | `cash`, `fixed_income`, `equity`, `etf`, `crypto`, `private_equity`, `other` |
| `ticker` | string \| null | no | Exchange ticker, when it has one |
| `quantity` | number \| null | no | Shares or units |
| `cost_basis` | number \| null | no | Average cost per unit, in `currency` |
| `amount` | number \| null | no | Total value, for holdings with no unit price. Not a market value |
| `currency` | string \| null | no | ISO currency code |
| `custodian` | string \| null | no | Who holds it. Part of the identity |
| `source` | string \| null | on create | `manual`, `interactive_brokers`, `coinbase`, `alpaca` |
| `as_of` | string \| null | on create | `YYYY-MM-DD`, the date the figures were true |
| `detail` | string \| null | no | Rate, maturity, vesting, strike. Not theses or price targets |

**Example call**

```python
await client.call_tool(
    name="upsertHolding",
    arguments={
        "name": "ACME", "kind": "equity", "ticker": "ACME",
        "quantity": 10, "cost_basis": 50.00, "currency": "USD",
        "custodian": "Example Broker",
        "source": "interactive_brokers", "as_of": "2026-01-15",
    },
)
```

**Returns**: The created or updated Holding object.

---

### `closeHolding`

Mark a position closed once it is sold, matured or otherwise gone. It keeps its history and
stops appearing in `getHoldings`.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `holding_id` | string | yes | The id of the holding to close |

**Returns**: A confirmation string, or a message if no open holding has that id.

---

## Ticker Record Tools

Why a name is interesting and what would make the agent act on it. This is the watchlist and
the conviction record in one. Disjoint from holdings and linked by ticker: holdings answer
*what and how much*, these answer *why, and at what price*.

### `getTickerRecords`

Return tracked names.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `status` | string \| null | no | Filter by `watching`, `held`, `exited` or `rejected`. Omit for all |

**Returns**: A list of Ticker Record objects.

---

### `upsertTickerRecord`

Record or update one name. Keyed by ticker and updated in place, so resetting an entry
trigger edits the existing record rather than adding a second one. Only the fields passed
are written.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `ticker` | string | yes | Exchange ticker, e.g. `LHX`, `ENR.DE`, `7011.T` |
| `status` | string \| null | on create | `watching`, `held`, `exited`, `rejected` |
| `thesis` | string \| null | no | Why the name is interesting |
| `entry_trigger` | string \| null | no | The condition that would make it a buy, checkable against live data |
| `falsifier` | string \| null | no | What would prove the thesis wrong |
| `notes` | string \| null | no | Anything else durable the other fields do not hold |

**Returns**: The created or updated Ticker Record object.

---

### `deleteTickerRecord`

Permanently remove a record. Prefer setting `status` to `rejected` or `exited`: why a name
was turned down is worth keeping. Use this only for a record created by mistake.

**Parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `ticker` | string | yes | The ticker whose record should be deleted |

**Returns**: A confirmation string, or a message if no record exists.

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

Returns the system prompt used to configure the InvestPal investment advisor agent.

**Parameters**

None. The server serves a single client, whose profile the agent loads through `getUserProfileNotes`.

**Example call**

```python
result = await client.get_prompt(
    name="get_invstment_advisor_prompt",
    arguments={},
)
print(result.messages[0].content.text)
```

**Returns**: The investment advisor system prompt string.

---

## Error Handling

The MCP server propagates errors as MCP tool error responses. In the FastMCP Python client, a failed tool call raises an exception. Common causes:

| Cause | Description |
|---|---|
| Invalid date format | Dates must be in `YYYY-MM-DD` format |
| Database unavailable | The turso database file could not be opened on startup |

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
| `TURSO_DB_PATH` | Path to the turso/SQLite database file. Defaults to `investpal.db` |
| `EMBEDDING_ENABLED` | Whether to load the local embedding model. Defaults to `true` |
| `EMBEDDING_MODEL_NAME` | fastembed model used for semantic search. Defaults to `BAAI/bge-small-en-v1.5` |
| `EMBEDDING_CACHE_DIR` | Where the model files are cached. Defaults to `~/.cache/investpal/fastembed` |
| `TURSO_SYNC_URL` | Optional Turso Cloud database to sync with. Unset means fully local. See [turso_sync.md](turso_sync.md) |
| `TURSO_SYNC_AUTH_TOKEN` | Token for that database |
| `TURSO_SYNC_CLIENT_NAME` | This device's sync identity. Must differ per device. Defaults to `investpal-<hostname>` |

With `TURSO_SYNC_URL` set, the server refuses to start until the local database has been initialised for sync with `make turso_first_push` or `make turso_first_pull`, because writes made before that would never reach the cloud.

---

## Semantic search

`searchUserConversationNotes` runs entirely on the local machine. There is no external vector store and no embedding API.

- **Vectors** live in the `user_conversation_note_embeddings` table and are compared with turso's built-in `vector_distance_cos`. The installed turso build has no ANN index, so this is a linear scan; that is intentional and comfortably fast at the scale conversation notes reach.
- **Embeddings** come from `BAAI/bge-small-en-v1.5` (384 dimensions) running on the CPU through fastembed's ONNX runtime. The model is roughly 67MB and is downloaded from HuggingFace the first time it is used, then served from `EMBEDDING_CACHE_DIR`.
- **After the first download**, set `HF_HUB_OFFLINE=1`. huggingface_hub otherwise makes a metadata call on every model load, which stalls startup when the machine is offline.
- The model loads in the background at server startup, so the first search does not pay for it.
- Set `EMBEDDING_ENABLED=false` to skip the model entirely. Notes can still be created and listed; `searchUserConversationNotes` returns an empty list.

Notes are embedded as they are created. Embedding failures are logged and never block note creation, so run `make backfill_embeddings` to pick up anything that was missed, and after any change to `EMBEDDING_MODEL_NAME`.
