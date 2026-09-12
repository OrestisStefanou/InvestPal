import platform
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
    # Tools whose output is large enough to be worth pacing (see
    # services/agents/middleware.py). Only InvestPal's own tools are named here.
    # The market data server's tool names belong to whichever provider is
    # configured, so they are supplied through the environment rather than
    # hardcoded, and a provider swap stays a config change.
    TOKEN_INTENSIVE_TOOLS: list[str] = [
        "getSkill",
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

    # TURSO CLOUD SYNC (optional)
    # Leave TURSO_SYNC_URL unset and the app stays fully local: plain turso file,
    # no sync engine, no network. Setting it turns every database connection into
    # a sync connection, so the local file must first be initialised with
    # `make turso_first_push` or `make turso_first_pull`.
    TURSO_SYNC_URL: str | None = None
    TURSO_SYNC_AUTH_TOKEN: str | None = None
    # Must differ per device: the remote tracks the last pushed change per
    # client_id, so two devices sharing a name lose each other's changes.
    TURSO_SYNC_CLIENT_NAME: str | None = None

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def turso_cloud_enabled(self) -> bool:
        return bool(self.TURSO_SYNC_URL)

    @property
    def turso_sync_url(self) -> str | None:
        """The remote URL in a scheme the sync engine can actually dial.

        `turso db show --url` prints turso://, the dashboard sometimes prints
        libsql://, and pyturso 0.6.1 only rewrites the latter. An unrewritten
        turso:// reaches urllib and fails with "unknown url type", so both are
        normalised here and the .env can hold whichever form was copied.
        """
        url = self.TURSO_SYNC_URL
        if url is None:
            return None
        for scheme in ("turso://", "libsql://", "wss://", "ws://"):
            if url.startswith(scheme):
                return "https://" + url[len(scheme):]
        return url

    @property
    def turso_sync_client_name(self) -> str:
        return self.TURSO_SYNC_CLIENT_NAME or f"investpal-{platform.node() or 'unknown'}"

settings = Settings()
