"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    github_app_id: int
    github_app_private_key: str
    github_app_webhook_secret: str

    model_config = {"env_prefix": "", "env_file": ".env", "env_file_encoding": "utf-8"}


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()
