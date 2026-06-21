import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

from app.main import create_app
from app.services.installation_service import InstallationService


@pytest.fixture(autouse=True)
def _required_env(monkeypatch):
    """Provide required settings for tests when not overridden."""
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/translation",
    )
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("RQ_QUEUE_NAME", "translation")


@pytest.fixture
def mock_installation_service():
    """Provide a mock InstallationService for tests that don't need persistence."""
    service = AsyncMock(spec=InstallationService)
    service.verify_and_persist = AsyncMock(return_value={
        "installation_id": 0,
        "account_login": "",
        "account_type": "",
    })
    return service


@pytest.fixture
def app(mock_installation_service):
    return create_app(installation_service=mock_installation_service)


@pytest.fixture
def client(app):
    return TestClient(app)
