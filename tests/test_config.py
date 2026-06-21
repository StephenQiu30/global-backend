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


def test_settings_has_database_url_default(monkeypatch):
    """Settings must expose database_url with local-development default."""
    monkeypatch.setenv("GITHUB_APP_ID", "12345")
    monkeypatch.setenv("GITHUB_PRIVATE_KEY", "test-key")
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "test-secret")

    from app.core.config import Settings

    settings = Settings()
    assert settings.database_url == "postgresql+psycopg://postgres:postgres@localhost:5432/global_backend"


def test_settings_database_url_env_override(monkeypatch):
    """Settings must allow DATABASE_URL environment variable to override default."""
    monkeypatch.setenv("GITHUB_APP_ID", "12345")
    monkeypatch.setenv("GITHUB_PRIVATE_KEY", "test-key")
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "test-secret")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:pass@db:5432/prod")

    from app.core.config import Settings

    settings = Settings()
    assert settings.database_url == "postgresql+psycopg://user:pass@db:5432/prod"


def test_settings_has_redis_url_default(monkeypatch):
    """Settings must expose redis_url with local-development default."""
    monkeypatch.setenv("GITHUB_APP_ID", "12345")
    monkeypatch.setenv("GITHUB_PRIVATE_KEY", "test-key")
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "test-secret")


    from app.core.config import Settings

    settings = Settings()
    assert settings.redis_url == "redis://localhost:6379/0"


def test_settings_redis_url_env_override(monkeypatch):
    """Settings must allow REDIS_URL environment variable to override default."""
    monkeypatch.setenv("GITHUB_APP_ID", "12345")
    monkeypatch.setenv("GITHUB_PRIVATE_KEY", "test-key")
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "test-secret")
    monkeypatch.setenv("REDIS_URL", "redis://redis.prod:6379/1")

    from app.core.config import Settings

    settings = Settings()
    assert settings.redis_url == "redis://redis.prod:6379/1"


def test_settings_has_rq_queue_name_default(monkeypatch):
    """Settings must expose rq_queue_name with 'default' value."""
    monkeypatch.setenv("GITHUB_APP_ID", "12345")
    monkeypatch.setenv("GITHUB_PRIVATE_KEY", "test-key")
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "test-secret")

    from app.core.config import Settings

    settings = Settings()
    assert settings.rq_queue_name == "default"


def test_settings_rq_queue_name_env_override(monkeypatch):
    """Settings must allow RQ_QUEUE_NAME environment variable to override default."""
    monkeypatch.setenv("GITHUB_APP_ID", "12345")
    monkeypatch.setenv("GITHUB_PRIVATE_KEY", "test-key")
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "test-secret")
    monkeypatch.setenv("RQ_QUEUE_NAME", "translations")

    from app.core.config import Settings

    settings = Settings()
    assert settings.rq_queue_name == "translations"
