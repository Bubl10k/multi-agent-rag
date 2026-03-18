from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthConfig(BaseSettings):
    JWT_SECRET: str
    JWT_LIFETIME_SECONDS: int = 3600

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
