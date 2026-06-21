"""Shared GitHub App client factory."""

from app.core.config import Settings
from app.services.github_app import GitHubAppClient


def get_github_client() -> GitHubAppClient:
    """Create a GitHubAppClient from current settings."""
    settings = Settings()
    return GitHubAppClient(
        app_id=settings.github_app_id,
        private_key=settings.github_private_key,
    )
