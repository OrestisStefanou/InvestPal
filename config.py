from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict

class LLMProvider(str, Enum):
    OPENAI = "openai"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"


class Settings(BaseSettings):
    # LLM
    LLM_PROVIDER: LLMProvider   # Default LLM provider
    LLM_MODEL: str              # Default LLM model
    OPENAI_API_KEY: str | None = None
    GOOGLE_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    TEMPERATURE: float = 0.1
    # MCP
    MARKET_DATA_MCP_SERVER_URL: str
    MARKET_DATA_MCP_SERVER_NAME: str = "market_data_tools"

    ALPACA_MCP_SERVER_URL: str | None = None
    ALPACA_MCP_SERVER_NAME: str = "alpaca_markets_tools"

    COINBASE_MCP_SERVER_URL: str | None = None
    COINBASE_MCP_SERVER_NAME: str = "coinbase_markets_tools"

    # APP
    CONVERSATION_MESSAGES_LIMIT: int = 15
    TOKEN_INTENSIVE_TOOLS: list[str] = [
        "getSkill",
        "getMarketNews",
        "getStockFinancials",
        "getInsiderTransactions",
        "getCompanyKpiMetrics",
        "getUserConversationNotes",
        "getWorkflowResults",
        "getCryptocurrencyNews",
        "getCryptocurrencyDataById",
    ]
    
    INVESTMENT_MANAGER_LLM_PROVIDER: LLMProvider = LLMProvider.ANTHROPIC
    INVESTMENT_MANAGER_LLM_MODEL: str = "claude-sonnet-4-6"
    INVESTMENT_MANAGER_TEMPERATURE: float = 0.1

    USER_CONTEXT_MEMORY_MANAGER_LLM_PROVIDER: LLMProvider = LLMProvider.ANTHROPIC
    USER_CONTEXT_MEMORY_MANAGER_LLM_MODEL: str = "claude-haiku-4-5"
    USER_CONTEXT_MEMORY_MANAGER_TEMPERATURE: float = 0.1

    # TODO: Add a section here for the workflow execution agent
    WORKFLOW_EXECUTION_AGENT_LLM_PROVIDER: LLMProvider = LLMProvider.ANTHROPIC
    WORKFLOW_EXECUTION_AGENT_LLM_MODEL: str = "claude-sonnet-4-6"
    WORKFLOW_EXECUTION_AGENT_TEMPERATURE: float = 0.1


    # EMBEDDINGS
    # Local ONNX embedding model used for semantic search over conversation notes.
    # The dimension count is not configurable here on purpose: schema.sql hardcodes
    # F32_BLOB(384), so it lives next to that assumption in repos/embeddings.py.
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_CACHE_DIR: str = "~/.cache/investpal/fastembed"
    EMBEDDING_ENABLED: bool = True

    # MCP APP
    TURSO_DB_PATH: str = "investpal.db"
    MCP_APP_SERVER_PORT: int = 9000

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
