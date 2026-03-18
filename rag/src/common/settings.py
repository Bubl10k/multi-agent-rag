from pydantic_settings import BaseSettings, SettingsConfigDict

from rag.src.common.app import AppConfig
from rag.src.common.db import DBConfig
from rag.src.common.llm import LLMConfig


class Settings(BaseSettings):
    app: AppConfig = AppConfig()
    database: DBConfig = DBConfig()
    llm: LLMConfig = LLMConfig()

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
