from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentConfig(BaseSettings):
    TAVILY_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
