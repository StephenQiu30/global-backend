"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """GitHub App, persistence, and application settings."""

    github_app_id: str = ""
    github_private_key: str = ""
    github_webhook_secret: str = ""
    database_url: str = "sqlite+aiosqlite:///./test.db"

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/global_backend"
    redis_url: str = "redis://localhost:6379/0"
    rq_queue_name: str = "default"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }
