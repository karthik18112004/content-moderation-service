"""Shared configuration from environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/moderation_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Rate Limiting (Token Bucket) - API only
    rate_limit_tokens_per_minute: int = 5
    rate_limit_bucket_capacity: int = 5

    # Message queue channel
    moderation_events_channel: str = "content-moderation-events"

    # Optional API key - API only
    api_key: str | None = None

    # API service
    api_host: str = "0.0.0.0"
    api_port: int = 8000


settings = Settings()
