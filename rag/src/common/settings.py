from pydantic_settings import BaseSettings, SettingsConfigDict

from rag.src.common.agent import AgentConfig
from rag.src.common.app import AppConfig
from rag.src.common.auth import AuthConfig
from rag.src.common.crypto import CryptoConfig
from rag.src.common.db import DBConfig
from rag.src.common.llm import LLMConfig
from rag.src.common.platform_llm import PlatformLLMConfig
from rag.src.common.s3 import S3Config


class Settings(BaseSettings):
    app: AppConfig = AppConfig()
    database: DBConfig = DBConfig()
    llm: LLMConfig = LLMConfig()
    auth: AuthConfig = AuthConfig()
    crypto: CryptoConfig = CryptoConfig()
    agent: AgentConfig = AgentConfig()
    s3: S3Config = S3Config()
    platform_llm: PlatformLLMConfig = PlatformLLMConfig()

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
