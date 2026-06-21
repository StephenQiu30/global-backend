"""Application configuration loaded from environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application settings. Values are loaded from environment / `.env` only."""

    github_app_id: str = ""
    github_private_key: str = ""
    github_webhook_secret: str = ""
    database_url: str
    redis_url: str
    rq_queue_name: str

    model_config = {
        "env_file": str(ENV_FILE),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }
