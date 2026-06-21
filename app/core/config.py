"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings. Values are loaded from environment / `.env` only."""

    github_app_id: str = ""
    github_private_key: str = ""
    github_webhook_secret: str = ""
    database_url: str
    redis_url: str
    rq_queue_name: str

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }
