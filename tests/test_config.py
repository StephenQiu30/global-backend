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


def test_settings_optional_private_key_defaults_empty(monkeypatch):
    """GitHub private key may be empty when not configured."""
    monkeypatch.setenv("GITHUB_APP_ID", "12345")
    monkeypatch.delenv("GITHUB_PRIVATE_KEY", raising=False)
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "test-secret")

    from app.core.config import Settings

    settings = Settings()
    assert settings.github_private_key == ""


def test_settings_loads_database_url_from_env(monkeypatch):
    """Settings must load DATABASE_URL from environment."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:pass@db:5432/prod")

    from app.core.config import Settings

    settings = Settings()
    assert settings.database_url == "postgresql+psycopg://user:pass@db:5432/prod"


def test_settings_loads_redis_url_from_env(monkeypatch):
    """Settings must load REDIS_URL from environment."""
    monkeypatch.setenv("REDIS_URL", "redis://redis.prod:6379/1")

    from app.core.config import Settings

    settings = Settings()
    assert settings.redis_url == "redis://redis.prod:6379/1"


def test_settings_loads_rq_queue_name_from_env(monkeypatch):
    """Settings must load RQ_QUEUE_NAME from environment."""
    monkeypatch.setenv("RQ_QUEUE_NAME", "translations")

    from app.core.config import Settings

    settings = Settings()
    assert settings.rq_queue_name == "translations"


def test_settings_requires_database_url(monkeypatch):
    """Settings must fail when DATABASE_URL is missing."""
    monkeypatch.delenv("DATABASE_URL", raising=False)

    from app.core.config import Settings

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
