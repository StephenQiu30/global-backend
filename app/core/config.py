"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """GitHub App and application settings."""

    github_app_id: str = ""
    github_private_key: str = ""
    github_webhook_secret: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
