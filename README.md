# InvestPal

InvestPal is an AI-powered investment advisor service. It exposes a REST API for client applications and an MCP server for AI agent integrations. It uses FastAPI, MongoDB, LangChain, and the Model Context Protocol (MCP) to deliver personalized investment insights backed by real-time market data.

## Features

- **AI Investment Advisor**: Personalized investment insights powered by state-of-the-art LLMs (OpenAI, Google, Anthropic).
- **Session Management**: Persistent, per-user conversation history stored in MongoDB.
- **Conversation Memory**: Agent recalls key details from past sessions via a dedicated notes system.
- **Reminders**: Agent can create and manage time-sensitive action items for users across sessions.
- **User Context**: Store and update user profiles to inform personalized advice.
- **MCP Integration**: Extensible tool system for market data, stock profiles, forecasts, and more.
- **Alpaca Markets Integration**: Execute orders, read portfolio holdings, and manage positions.
- **Coinbase Integration**: Manage crypto portfolios and execute trades.
- **Internal MCP Server**: Exposes user context, conversation memory, and reminder tools to the agent.

## Tech Stack

| Layer | Technology |
|---|---|
| REST API | [FastAPI](https://fastapi.tiangolo.com/) |
| Database | [MongoDB](https://www.mongodb.com/) |
| AI Framework | [LangChain](https://www.langchain.com/) |
| MCP Protocol | [Model Context Protocol](https://modelcontextprotocol.io/) |
| MCP Framework | [FastMCP](https://github.com/jlowin/fastmcp) |
| Dependency Management | [uv](https://github.com/astral-sh/uv) |

## Prerequisites

- Python 3.13+
- MongoDB instance (Atlas or local)
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
   # MongoDB
   MONGO_URI=mongodb://localhost:27017
   MONGO_DB_NAME=investpal
   USER_CONTEXT_COLLECTION_NAME=user_contexts
   SESSION_COLLECTION_NAME=sessions
   USER_CONVERSATION_NOTES_COLLECTION_NAME=user_conversation_notes
   AGENT_REMINDERS_COLLECTION_NAME=agent_reminders

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
   CONVERSATION_MESSAGES_LIMIT=15
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

Both servers share the same MongoDB database and must point to the same `MONGO_URI`.

## API Documentation

| Document | Description |
|---|---|
| [docs/rest_api.md](docs/rest_api.md) | REST API — endpoints for chat, sessions, and user context |
| [docs/mcp_api.md](docs/mcp_api.md) | MCP API — tools and prompts for agent integrations |

### REST API quick reference

```
POST   /user_context           Register a user (required before opening sessions)
GET    /user_context/{user_id} Get user profile
PUT    /user_context           Update user profile

POST   /session                Create a conversation session
GET    /session/{session_id}   Get session with full message history
GET    /sessions/{user_id}     List all sessions for a user

POST   /chat                   Send a message and receive an AI response
```

### MCP tools quick reference

| Tool | Description |
|---|---|
| `getUserContext` | Fetch a user's profile |
| `updateUserContext` | Replace a user's profile |
| `getUserConversationNotes` | Retrieve notes from past conversations |
| `updateUserConversationNotes` | Store/merge notes for a conversation date |
| `createAgentReminder` | Create a reminder for a user |
| `getAgentReminders` | List all reminders for a user |
| `updateAgentReminder` | Update a reminder's description or due date |
| `deleteAgentReminder` | Delete a reminder |

## Project Structure

```
.
├── main.py                  # REST API entry point and FastAPI app setup
├── config.py                # Settings (loaded from .env via pydantic-settings)
├── dependencies.py          # Dependency injection (DB client, MCP clients, services)
├── apps/
│   ├── rest_api/            # REST API route handlers (chat, session, user_context)
│   └── mcp_api/             # MCP server (tools, prompts, lifespan)
├── services/
│   ├── agents/              # LangChain agent definitions and prompts
│   ├── agent_service.py     # Orchestrates agent + memory manager per request
│   ├── chat.py              # Chat service (session + agent coordination)
│   ├── session.py           # Session persistence
│   ├── user_context.py      # User context and conversation notes persistence
│   └── agent_reminder.py    # Reminder persistence
├── models/                  # Internal Pydantic data models
└── docs/
    ├── rest_api.md          # REST API reference
    └── mcp_api.md           # MCP API reference
```
