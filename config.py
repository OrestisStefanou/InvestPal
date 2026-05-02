from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict

class LLMProvider(str, Enum):
    OPENAI = "openai"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"


class Settings(BaseSettings):
    # MongoDB
    MONGO_URI: str
    MONGO_DB_NAME: str
    USER_CONTEXT_COLLECTION_NAME: str = "user_context"
    SESSION_COLLECTION_NAME: str = "session"
    USER_CONVERSATION_NOTES_COLLECTION_NAME: str = "user_conversation_notes"
    AGENT_REMINDERS_COLLECTION_NAME: str = "agent_reminders"
    AGENT_WORKFLOWS_COLLECTION_NAME: str = "agent_workflows"
    WORKFLOW_RESULTS_COLLECTION_NAME: str = "workflow_results"
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
        "getEarningsCallTranscript",
        "getInsiderTransactions",
        "getCompanyKpiMetrics",
        "getUserConversationNotes",
        "getWorkflowResults",
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


    # MCP APP
    MCP_APP_SERVER_PORT: int = 9000

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
