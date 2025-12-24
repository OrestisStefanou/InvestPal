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
    USER_CONTEXT_COLLECTION_NAME: str
    SESSION_COLLECTION_NAME: str
    # LLM
    LLM_PROVIDER: LLMProvider
    LLM_MODEL: str
    OPENAI_API_KEY: str | None = None
    GOOGLE_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    TEMPERATURE: float = 0.1
    # MCP
    MCP_SERVER_URL: str
    MCP_SERVER_NAME: str = "investing_data_tools"
    # APP
    CONVERSATION_MESSAGES_LIMIT: int = 15

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
