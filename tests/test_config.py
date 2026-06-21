import pytest
from pydantic import ValidationError


def test_settings_loads_from_env(monkeypatch):
    """Settings must load GitHub App credentials from environment."""
    monkeypatch.setenv("GITHUB_APP_ID", "12345")
    monkeypatch.setenv("GITHUB_PRIVATE_KEY", "test-key")
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "test-secret")

    from app.core.config import Settings

    settings = Settings()
    assert settings.github_app_id == "12345"
    assert settings.github_private_key == "test-key"
    assert settings.github_webhook_secret == "test-secret"


def test_settings_allows_unrelated_env_vars(monkeypatch):
    """Settings must ignore unrelated environment variables such as Symphony config."""
    monkeypatch.setenv("GITHUB_APP_ID", "12345")
    monkeypatch.setenv("GITHUB_PRIVATE_KEY", "test-key")
    monkeypatch.setenv("SYMPHONY_PORT", "4000")

    from app.core.config import Settings

    settings = Settings()
    assert settings.github_app_id == "12345"


def test_settings_requires_private_key(monkeypatch):
    """Settings must fail when GITHUB_PRIVATE_KEY is missing if required."""
    monkeypatch.setenv("GITHUB_APP_ID", "12345")
    monkeypatch.delenv("GITHUB_PRIVATE_KEY", raising=False)
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "test-secret")

    from app.core.config import Settings

    settings = Settings()
    assert settings.github_private_key == ""
