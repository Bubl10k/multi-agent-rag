from pydantic_settings import BaseSettings, SettingsConfigDict


class PlatformLLMConfig(BaseSettings):
    OPENAI_PLATFORM_API_KEY: str
    GOOGLE_PLATFORM_API_KEY: str
    PLATFORM_LLM_HOURLY_LIMIT: int = 10

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
