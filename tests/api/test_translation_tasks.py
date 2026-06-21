"""Tests for POST /api/translation-tasks endpoint."""

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.models.base import Base
from app.main import create_app
from app.repositories.translation_task_repository import TranslationTaskRepository
from app.queues.translation_task_queue import StubTranslationTaskQueue
from app.services.translation_task_service import TranslationTaskService
from fastapi.testclient import TestClient


@pytest.fixture
async def db_engine():
    """Create an in-memory SQLite async engine for testing."""
    eng = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest.fixture
async def db_session(db_engine):
    """Create an async session for testing."""
    factory = async_sessionmaker(db_engine, expire_on_commit=False)
    async with factory() as sess:
        yield sess


@pytest.fixture
def queue():
    """Create a stub queue for testing."""
    return StubTranslationTaskQueue()


@pytest.fixture
async def task_service(db_session, queue):
    """Create a TranslationTaskService for testing."""
    repo = TranslationTaskRepository(db_session)
    return TranslationTaskService(repo, queue)


@pytest.fixture
def app(task_service):
    """Create a test app with the task service wired."""
    return create_app(task_service=task_service)


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


class TestTranslationTasksSuccess:
    """Tests for successful translation task creation."""

    def test_create_task_single_file(self, client):
        """POST /api/translation-tasks returns task_id and queued status."""
        response = client.post("/api/translation-tasks", json={
            "installation_id": "inst-123",
            "repository": "owner/repo",
            "base_branch": "main",
            "files": ["README.md"],
            "language": "zh-CN",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["code"] == "SUCCESS"
        assert data["message"] == "OK"
        assert "trace_id" in data
        assert "task_id" in data["data"]
        assert data["data"]["status"] == "queued"
        assert len(data["data"]["task_id"]) == 36  # uuid4() with hyphens

    def test_create_task_multiple_files(self, client):
        """POST /api/translation-tasks with multiple files returns task_id."""
        response = client.post("/api/translation-tasks", json={
            "installation_id": "inst-456",
            "repository": "org/project",
            "base_branch": "develop",
            "files": ["README.md", "docs/guide.md"],
            "language": "ja",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["status"] == "queued"


class TestTranslationTasksValidation:
    """Tests for request validation."""

    def test_missing_installation_id(self, client):
        response = client.post("/api/translation-tasks", json={
            "repository": "owner/repo",
            "base_branch": "main",
            "files": ["README.md"],
            "language": "zh-CN",
        })
        assert response.status_code == 422

    def test_missing_repository(self, client):
        response = client.post("/api/translation-tasks", json={
            "installation_id": "inst-123",
            "base_branch": "main",
            "files": ["README.md"],
            "language": "zh-CN",
        })
        assert response.status_code == 422

    def test_missing_files(self, client):
        response = client.post("/api/translation-tasks", json={
            "installation_id": "inst-123",
            "repository": "owner/repo",
            "base_branch": "main",
            "language": "zh-CN",
        })
        assert response.status_code == 422

    def test_empty_files_list(self, client):
        response = client.post("/api/translation-tasks", json={
            "installation_id": "inst-123",
            "repository": "owner/repo",
            "base_branch": "main",
            "files": [],
            "language": "zh-CN",
        })
        assert response.status_code == 422

    def test_missing_language(self, client):
        response = client.post("/api/translation-tasks", json={
            "installation_id": "inst-123",
            "repository": "owner/repo",
            "base_branch": "main",
            "files": ["README.md"],
        })
        assert response.status_code == 422

    def test_missing_base_branch(self, client):
        response = client.post("/api/translation-tasks", json={
            "installation_id": "inst-123",
            "repository": "owner/repo",
            "files": ["README.md"],
            "language": "zh-CN",
        })
        assert response.status_code == 422

    def test_empty_installation_id(self, client):
        response = client.post("/api/translation-tasks", json={
            "installation_id": "",
            "repository": "owner/repo",
            "base_branch": "main",
            "files": ["README.md"],
            "language": "zh-CN",
        })
        assert response.status_code == 422


class TestTranslationTasksLanguageValidation:
    """Tests for language code validation in translation tasks."""

    def test_unsupported_language_rejected(self, client):
        response = client.post("/api/translation-tasks", json={
            "installation_id": "inst-123",
            "repository": "owner/repo",
            "base_branch": "main",
            "files": ["README.md"],
            "language": "xx",
        })
        assert response.status_code == 400
        data = response.json()
        assert data["code"] == "UNSUPPORTED_LANGUAGE"
        assert "trace_id" in data
        assert data["data"] is None

    def test_empty_language_rejected(self, client):
        response = client.post("/api/translation-tasks", json={
            "installation_id": "inst-123",
            "repository": "owner/repo",
            "base_branch": "main",
            "files": ["README.md"],
            "language": "",
        })
        assert response.status_code == 422

    def test_similar_language_code_rejected(self, client):
        response = client.post("/api/translation-tasks", json={
            "installation_id": "inst-123",
            "repository": "owner/repo",
            "base_branch": "main",
            "files": ["README.md"],
            "language": "zh",
        })
        assert response.status_code == 400

    def test_uppercase_language_rejected(self, client):
        response = client.post("/api/translation-tasks", json={
            "installation_id": "inst-123",
            "repository": "owner/repo",
            "base_branch": "main",
            "files": ["README.md"],
            "language": "ZH-CN",
        })
        assert response.status_code == 400
