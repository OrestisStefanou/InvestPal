# InvestPal

InvestPal is an advanced AI-powered investment advisor service. It leverages FastAPI for the backend, MongoDB for data persistence, and LangChain to integrate various Large Language Models (LLMs) like OpenAI, Google Gemini, and Anthropic. It also uses the Model Context Protocol (MCP) and [MarketDataMcpServer](https://github.com/OrestisStefanou/MarketDataMcpServer) to access real-time investing data and tools.

## Features

- **AI Investment Advisor**: Personalized investment insights powered by state-of-the-art LLMs.
- **Session Management**: Persistent chat history stored in MongoDB.
- **Context Awareness**: Remembers user preferences and context for more relevant advice.
- **MCP Integration**: Extensible tool system to fetch market data, stock profiles, and forecasts.
- **Alpaca Markets Integration**: Execute orders, read portfolio holdings, and manage positions via Alpaca.
- **Coinbase Integration**: Manage crypto portfolios and execute trades via Coinbase.
- **Internal MCP Server**: Manages user context and provides specialized advisor prompts.
- **Multi-LLM Support**: Choose between OpenAI, Google, or Anthropic providers.

## Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: [MongoDB](https://www.mongodb.com/)
- **AI Framework**: [LangChain](https://www.langchain.com/)
- **MCP Protocol**: [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- **MCP Framework**: [FastMCP](https://github.com/jlowin/fastmcp)
- **Market Data MCP**: [MarketDataMcpServer](https://github.com/OrestisStefanou/MarketDataMcpServer)
- **Alpaca MCP**: Integration with Alpaca Markets for trading and portfolio access.
- **Coinbase MCP**: Integration with Coinbase for crypto trading and portfolio management.
- **Dependency Management**: [uv](https://github.com/astral-sh/uv)

## Prerequisites

- Python 3.13+
- MongoDB instance (Atlas or local)
- API Keys for your chosen LLM (OpenAI, Google, or Anthropic)
- Access to a [MarketDataMcpServer](https://github.com/OrestisStefanou/MarketDataMcpServer) instance providing investment data tools

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd InvestPal
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Configure environment variables**:
   Create a `.env` file in the root directory based on the following template:
   ```env
   # MongoDB
   MONGO_URI=mongodb://localhost:27017
   MONGO_DB_NAME=investpal
   USER_CONTEXT_COLLECTION_NAME=user_contexts
   SESSION_COLLECTION_NAME=sessions

   # LLM
   LLM_PROVIDER=openai # or google, anthropic
   LLM_MODEL=gpt-4o
   OPENAI_API_KEY=your_openai_key
   # GOOGLE_API_KEY=your_google_key
   # ANTHROPIC_API_KEY=your_anthropic_key
   TEMPERATURE=0.1

   # MCP
   MARKET_DATA_MCP_SERVER_URL=http://localhost:8000
   MARKET_DATA_MCP_SERVER_NAME=market_data_tools

   ALPACA_MCP_SERVER_URL=http://localhost:8001
   ALPACA_MCP_SERVER_NAME=alpaca_markets_tools

   COINBASE_MCP_SERVER_URL=http://localhost:8002
   COINBASE_MCP_SERVER_NAME=coinbase_markets_tools

   # APP
   CONVERSATION_MESSAGES_LIMIT=15
   ```

## Running the Application

Start the FastAPI server:

```bash
uv run fastapi dev main.py
```

The API will be available at `http://localhost:8000`. You can access the Interactive API docs at `http://localhost:8000/docs`.

### Internal MCP Server

InvestPal includes an internal MCP server to manage user-specific context and provide personalized prompts.

Start the internal MCP server:

```bash
uv run python -m apps.mcp_api.app
```

The server will be available at `http://localhost:9000`.

#### Tools Provided

- `getUserContext(user_id: str)`: Retrieves the user's profile and portfolio details.
- `updateUserContext(user_id: str, user_profile: dict, user_portfolio: list)`: Updates/Replaces the user's profile and portfolio.

#### Prompts Provided

- `get_invstment_advisor_prompt(user_id: str)`: Returns a professional investment advisor prompt tailored to the user's specific context.

## API Endpoints

### User Context
- `POST /user_context`: Upsert user context/preferences.
- `GET /user_context/{user_id}`: Retrieve user context.

### Session
- `POST /session`: Create a new session.
- `GET /session/{session_id}`: Retrieve session details.

### Chat
- `POST /chat`: Send a message to the AI advisor.
  - Request body: `{"session_id": "...", "message": "..."}`
  - Response: `{"response": "..."}`

## Project Structure
- `main.py`: Entry point and FastAPI app configuration.
- `apps/rest_api/`: API route definitions (chat, session, user_context).
- `services/`: Core business logic (agent orchestration, chat service, database interactions).
- `config.py`: Pydantic settings management.
- `dependencies.py`: Dependency injection for DB and MCP clients.
- `apps/mcp_api/`: Internal MCP server implementation.
- `models/`: Internal data models.
