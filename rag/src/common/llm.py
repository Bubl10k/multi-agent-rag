from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseSettings):
    OPENAI_API_SECRET: str
    OPENAI_MODEL: str = "gpt-4o"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )