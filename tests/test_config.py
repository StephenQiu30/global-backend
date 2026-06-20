import pytest
from pydantic import ValidationError


def test_settings_loads_from_env(monkeypatch):
    """Settings must load GitHub App credentials from environment."""
    monkeypatch.setenv("GITHUB_APP_ID", "12345")
    monkeypatch.setenv("GITHUB_APP_PRIVATE_KEY", "test-key")
    monkeypatch.setenv("GITHUB_APP_WEBHOOK_SECRET", "test-secret")

    from app.core.config import Settings

    settings = Settings()
    assert settings.github_app_id == 12345
    assert settings.github_app_private_key == "test-key"
    assert settings.github_app_webhook_secret == "test-secret"


def test_settings_requires_app_id(monkeypatch):
    """Settings must fail when GITHUB_APP_ID is missing."""
    monkeypatch.delenv("GITHUB_APP_ID", raising=False)
    monkeypatch.setenv("GITHUB_APP_PRIVATE_KEY", "test-key")
    monkeypatch.setenv("GITHUB_APP_WEBHOOK_SECRET", "test-secret")

    from app.core.config import Settings

    with pytest.raises(ValidationError):
        Settings()


def test_settings_requires_private_key(monkeypatch):
    """Settings must fail when GITHUB_APP_PRIVATE_KEY is missing."""
    monkeypatch.setenv("GITHUB_APP_ID", "12345")
    monkeypatch.delenv("GITHUB_APP_PRIVATE_KEY", raising=False)
    monkeypatch.setenv("GITHUB_APP_WEBHOOK_SECRET", "test-secret")

    from app.core.config import Settings

    with pytest.raises(ValidationError):
        Settings()
