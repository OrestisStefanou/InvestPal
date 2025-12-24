# InvestPal

InvestPal is an advanced AI-powered investment advisor service. It leverages FastAPI for the backend, MongoDB for data persistence, and LangChain to integrate various Large Language Models (LLMs) like OpenAI, Google Gemini, and Anthropic. It also uses the Model Context Protocol (MCP) to access real-time investing data and tools.

## Features

- **AI Investment Advisor**: Personalized investment insights powered by state-of-the-art LLMs.
- **Session Management**: Persistent chat history stored in MongoDB.
- **Context Awareness**: Remembers user preferences and context for more relevant advice.
- **MCP Integration**: Extensible tool system to fetch market data, stock profiles, and forecasts.
- **Multi-LLM Support**: Choose between OpenAI, Google, or Anthropic providers.

## Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: [MongoDB](https://www.mongodb.com/)
- **AI Framework**: [LangChain](https://www.langchain.com/)
- **Protocol**: [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- **Dependency Management**: [uv](https://github.com/astral-sh/uv)

## Prerequisites

- Python 3.13+
- MongoDB instance (Atlas or local)
- API Keys for your chosen LLM (OpenAI, Google, or Anthropic)
- Access to an MCP server providing investment data tools

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
   MCP_SERVER_URL=http://localhost:8000
   MCP_SERVER_NAME=investing_data_tools

   # APP
   CONVERSATION_MESSAGES_LIMIT=15
   ```

## Running the Application

Start the FastAPI server:

```bash
uv run fastapi dev main.py
```

The API will be available at `http://localhost:8000`. You can access the Interactive API docs at `http://localhost:8000/docs`.

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
- `routers/`: API route definitions (chat, session, user_context).
- `services/`: Core business logic (agent orchestration, chat service, database interactions).
- `config.py`: Pydantic settings management.
- `dependencies.py`: Dependency injection for DB and MCP clients.
