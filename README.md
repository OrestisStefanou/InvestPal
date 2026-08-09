# InvestPal

InvestPal is an AI-powered investment advisor service. It exposes a REST API for client applications and an MCP server for AI agent integrations. It uses FastAPI, turso, LangChain, and the Model Context Protocol (MCP) to deliver personalized investment insights backed by real-time market data.

## Features

- **AI Investment Advisor**: Personalized investment insights powered by state-of-the-art LLMs (OpenAI, Google, Anthropic).
- **Session Management**: Persistent conversation history stored in turso.
- **Conversation Memory**: Agent recalls key details from past sessions via a dedicated notes system, either chronologically or by semantic search.
- **Reminders**: Agent can create and manage time-sensitive action items across sessions.
- **Agent Workflows**: Run scheduled, autonomous workflows on the client's behalf (powered by cron).
- **User Profile**: Build up the client's profile as a set of notes to inform personalized advice.
- **MCP Integration**: Extensible tool system for market data, stock profiles, forecasts, and more.
- **Alpaca Markets Integration**: Execute orders, read portfolio holdings, and manage positions.
- **Coinbase Integration**: Manage crypto portfolios and execute trades.
- **Internal MCP Server**: Exposes user profile, conversation memory, and reminder tools to the agent.

## Tech Stack

| Layer | Technology |
|---|---|
| REST API | [FastAPI](https://fastapi.tiangolo.com/) |
| Database | [turso](https://turso.tech/) (embedded SQLite, with native vector search) |
| Embeddings | [fastembed](https://github.com/qdrant/fastembed) — `BAAI/bge-small-en-v1.5` on local ONNX runtime |
| AI Framework | [LangChain](https://www.langchain.com/) |
| MCP Protocol | [Model Context Protocol](https://modelcontextprotocol.io/) |
| MCP Framework | [FastMCP](https://github.com/jlowin/fastmcp) |
| Dependency Management | [uv](https://github.com/astral-sh/uv) |

## Prerequisites

- Python 3.13+
- API key for your chosen LLM provider (OpenAI, Google, or Anthropic)
- A running [MarketDataMcpServer](https://github.com/OrestisStefanou/MarketDataMcpServer) instance

## Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd InvestPal
   ```

2. **Install dependencies**

   ```bash
   uv sync
   ```

3. **Configure environment variables**

   Create a `.env` file in the root directory:

   ```env
   # LLM (choose one provider)
   LLM_PROVIDER=anthropic           # openai | google | anthropic
   LLM_MODEL=claude-sonnet-4-6
   ANTHROPIC_API_KEY=your_key
   # OPENAI_API_KEY=your_key
   # GOOGLE_API_KEY=your_key
   TEMPERATURE=0.1

   # Agent-specific LLM overrides (optional)
   INVESTMENT_MANAGER_LLM_PROVIDER=anthropic
   INVESTMENT_MANAGER_LLM_MODEL=claude-sonnet-4-6
   USER_CONTEXT_MEMORY_MANAGER_LLM_PROVIDER=anthropic
   USER_CONTEXT_MEMORY_MANAGER_LLM_MODEL=claude-haiku-4-5

   # MCP servers
   MARKET_DATA_MCP_SERVER_URL=http://localhost:8100
   # ALPACA_MCP_SERVER_URL=http://localhost:8101   # optional
   # COINBASE_MCP_SERVER_URL=http://localhost:8102  # optional

   # App
   TURSO_DB_PATH=investpal.db
   CONVERSATION_MESSAGES_LIMIT=15

   # Turso Cloud sync (optional; unset means fully local, no network)
   # TURSO_SYNC_URL=turso://your-db-your-org.turso.io
   # TURSO_SYNC_AUTH_TOKEN=your_token
   # TURSO_SYNC_CLIENT_NAME=laptop        # must differ on each device
   ```

## Running the Application

### REST API

```bash
uv run fastapi dev main.py
```

Available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### MCP Server

```bash
uv run python -m apps.mcp_api.app
```

Available at `http://localhost:9000/mcp`.

Both servers share the same turso database file and must point to the same `TURSO_DB_PATH`.

### Semantic search over conversation notes

`searchUserConversationNotes` finds notes by meaning rather than by date. It runs fully locally: vectors are stored in turso and compared with its built-in `vector_distance_cos`, and embeddings come from a ~67MB ONNX model on the CPU. No note text is sent anywhere.

The model is downloaded from HuggingFace on first use and cached in `EMBEDDING_CACHE_DIR` (default `~/.cache/investpal/fastembed`). Once that has happened, set `HF_HUB_OFFLINE=1` so model loads do not make a network call. Set `EMBEDDING_ENABLED=false` to skip the model altogether; notes can still be created and listed, but search returns nothing.

Notes are embedded as they are created. To re-embed everything after changing `EMBEDDING_MODEL_NAME`, or to pick up notes whose embedding failed:

```bash
make backfill_embeddings
```

### Turso Cloud sync (optional)

By default everything lives in one local file and never leaves the machine. Set `TURSO_SYNC_URL` and you can also keep a copy in [Turso Cloud](https://turso.tech) and move it between devices. Nothing syncs on its own: there is no sync on startup, no background timer, only the commands below.

Create a database in Turso Cloud, then put its URL and a token in `.env`:

```bash
TURSO_SYNC_URL=turso://your-db-your-org.turso.io   # turso db show <name> --url
TURSO_SYNC_AUTH_TOKEN=your_token                   # turso db tokens create <name>
TURSO_SYNC_CLIENT_NAME=laptop                      # must differ on each device
```

Then, depending on where you are starting from:

| Situation | Command |
|---|---|
| You already have a populated `investpal.db` and an empty cloud database | `make turso_first_push` |
| New device, no local database yet | `make turso_first_pull` |
| Send local changes to the cloud | `make turso_push` |
| Apply cloud changes locally | `make turso_pull` |
| Where am I, and what comes next | `make turso_status` |
| Compare local against the cloud copy | `make turso_verify` |

`make turso_first_push` is not the same as `make turso_push`: rows written before sync was switched on are invisible to the sync engine, so the first push has to rebuild the local file as a sync database and replay every row into it. It backs the original up first and reconciles row counts against the cloud when it finishes.

Once `TURSO_SYNC_URL` is set, both servers refuse to start until `make turso_first_push` or `make turso_first_pull` has run, because writes made in between would never reach the cloud. Stop both servers before running anything other than `status`, `verify` and `push`.

See [docs/turso_sync.md](docs/turso_sync.md) for the full runbook: conflict behaviour, the sidecar files, recovery, and how to rehearse it all against a local sync server without a Turso account.

## API Documentation

| Document | Description |
|---|---|
| [docs/rest_api.md](docs/rest_api.md) | REST API — endpoints for chat, sessions, reminders and workflows |
| [docs/mcp_api.md](docs/mcp_api.md) | MCP API — tools and prompts for agent integrations |
| [docs/turso_sync.md](docs/turso_sync.md) | Turso Cloud sync — pushing and pulling the database between devices |

### REST API quick reference

```
POST   /session                Create a conversation session
GET    /session/{session_id}   Get session with full message history
GET    /sessions               List all sessions

POST   /chat                   Send a message and receive an AI response

POST   /workflows              Create a new scheduled workflow
GET    /workflows              List scheduled workflows
PATCH  /workflows/{id}         Update a workflow
DELETE /workflows/{id}         Delete a workflow
POST   /workflows/check-and-run Execute due workflows (heartbeat)
GET    /workflow_results       Results of past workflow runs
```

### MCP tools quick reference

| Tool | Description |
|---|---|
| `getUserProfileNotes` | Fetch the notes that make up the user's profile |
| `createUserProfileNote` | Store a permanent fact about the user |
| `markUserProfileNoteAsOutdated` | Retire a profile fact that is no longer true |
| `getUserConversationNotes` | Retrieve notes from past conversations |
| `searchUserConversationNotes` | Search past conversation notes by meaning |
| `createUserConversationNote` | Store a note for a conversation date |
| `createAgentReminder` | Create a reminder for a user |
| `getAgentReminders` | List all reminders for a user |
| `updateAgentReminder` | Update a reminder's description or due date |
| `deleteAgentReminder` | Delete a reminder |
| `createAgentWorkflow` | Create a new scheduled workflow |
| `getAgentWorkflows` | List all workflows |
| `updateAgentWorkflow` | Update an existing workflow |
| `deleteAgentWorkflow` | Delete a workflow |
| `getWorkflowResults` | Get results of past workflow runs |
| `storeWorkflowResult` | Store a run's result, which also advances the workflow's next run |

## Project Structure

```
.
├── main.py                  # REST API entry point and FastAPI app setup
├── config.py                # Settings (loaded from .env via pydantic-settings)
├── dependencies.py          # Dependency injection (DB client, MCP clients, services)
├── apps/
│   ├── rest_api/            # REST API route handlers (chat, session, reminders, workflows)
│   └── mcp_api/             # MCP server (tools, prompts, lifespan)
├── services/
│   ├── agents/              # LangChain agent definitions and prompts
│   ├── agent_service.py     # Orchestrates agent + memory manager per request
│   ├── chat.py              # Chat service (session + agent coordination)
│   ├── session.py           # Session persistence
│   ├── user_context.py      # User profile and conversation notes persistence
│   └── agent_reminder.py    # Reminder persistence
├── repos/                   # One class per database table, plus shared infra
│   ├── db.py                # Connections, transactions and schema init
│   └── embeddings.py        # Local ONNX embedding model for semantic search
├── models/                  # Internal Pydantic data models
├── scripts/                 # One-off maintenance scripts (embeddings backfill, cloud sync)
└── docs/
    ├── rest_api.md          # REST API reference
    └── mcp_api.md           # MCP API reference
```
