from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    base_url: str = "http://localhost:8000"
    default_ttl_seconds: int = 86400
    max_ttl_seconds: int = 2592000
    short_code_length: int = 6
    cleanup_interval_seconds: int = 300
    database_url: str = "postgresql+asyncpg://user:pass@localhost/db"


settings = Settings()
