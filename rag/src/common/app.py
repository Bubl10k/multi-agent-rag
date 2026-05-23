from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    HOST: str
    PORT: int
    RELOAD: bool
    ALLOWED_ORIGINS: list[str]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
