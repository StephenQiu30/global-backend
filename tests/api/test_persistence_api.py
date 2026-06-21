"""Tests for persistence-integrated API endpoints.

Validates:
- POST /api/translation-tasks returns task_id + queued status
- GET /api/translation-tasks/{task_id} returns persisted status
- GET /api/translation-tasks/{task_id}/file-previews returns file metadata
- Unknown task IDs return task_not_found errors
- POST /api/github/installations/verify persists account metadata
"""

import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.models.base import Base
from app.models.installation_account import InstallationAccountModel
from app.repositories.translation_task_repository import TranslationTaskRepository
from app.repositories.installation_account_repository import InstallationAccountRepository
from app.queues.translation_task_queue import StubTranslationTaskQueue
from app.services.translation_task_service import TranslationTaskService
from app.services.installation_service import InstallationService
from app.main import create_app
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
async def installation_service(db_session):
    """Create an InstallationService for testing."""
    repo = InstallationAccountRepository(db_session)
    return InstallationService(repo)


@pytest.fixture
def app(task_service, installation_service):
    """Create a test app with services wired."""
    return create_app(
        task_service=task_service,
        installation_service=installation_service,
    )


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


class TestCreateTranslationTaskPersistence:
    """Tests for POST /api/translation-tasks with persistence."""

    def test_create_task_returns_task_id_and_queued_status(self, client):
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

    def test_create_task_enqueues_task_id(self, client, queue):
        """POST /api/translation-tasks enqueues the task ID."""
        response = client.post("/api/translation-tasks", json={
            "installation_id": "inst-123",
            "repository": "owner/repo",
            "base_branch": "main",
            "files": ["README.md"],
            "language": "zh-CN",
        })
        data = response.json()
        assert data["data"]["task_id"] in queue.enqueued_ids

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

    def test_create_task_unsupported_language(self, client):
        """POST /api/translation-tasks with unsupported language returns 400."""
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

    def test_create_task_validation_error(self, client):
        """POST /api/translation-tasks with missing fields returns 422."""
        response = client.post("/api/translation-tasks", json={
            "repository": "owner/repo",
            "base_branch": "main",
            "files": ["README.md"],
            "language": "zh-CN",
        })
        assert response.status_code == 422


class TestGetTaskStatus:
    """Tests for GET /api/translation-tasks/{task_id}."""

    def test_get_task_status_queued(self, client):
        """GET returns queued status for a newly created task."""
        create_resp = client.post("/api/translation-tasks", json={
            "installation_id": "inst-123",
            "repository": "owner/repo",
            "base_branch": "main",
            "files": ["README.md"],
            "language": "zh-CN",
        })
        task_id = create_resp.json()["data"]["task_id"]

        response = client.get(f"/api/translation-tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "SUCCESS"
        assert data["data"]["task_id"] == task_id
        assert data["data"]["status"] == "queued"
        assert data["data"]["repository"] == "owner/repo"
        assert data["data"]["language"] == "zh-CN"

    def test_get_task_status_with_result(self, client, task_service, db_session):
        """GET returns succeeded status with result fields."""
        create_resp = client.post("/api/translation-tasks", json={
            "installation_id": "inst-123",
            "repository": "owner/repo",
            "base_branch": "main",
            "files": ["README.md"],
            "language": "zh-CN",
        })
        task_id = create_resp.json()["data"]["task_id"]

        import asyncio
        from app.domain.task import TaskStatus

        async def update():
            repo = TranslationTaskRepository(db_session)
            await repo.update_status(
                task_id,
                TaskStatus.SUCCEEDED,
                pr_url="https://github.com/owner/repo/pull/42",
                pr_number=42,
                mappings=[{"source_path": "README.md", "target_path": "README.zh-CN.md"}],
            )
        asyncio.get_event_loop().run_until_complete(update())

        response = client.get(f"/api/translation-tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "succeeded"
        assert data["data"]["pr_url"] == "https://github.com/owner/repo/pull/42"
        assert data["data"]["pr_number"] == 42
        assert len(data["data"]["file_mappings"]) == 1

    def test_get_task_status_not_found(self, client):
        """GET returns 404 for unknown task_id."""
        response = client.get("/api/translation-tasks/nonexistent-task-id")
        assert response.status_code == 404
        data = response.json()
        assert data["code"] == "TASK_NOT_FOUND"
        assert "trace_id" in data
        assert data["data"] is None

    def test_get_task_status_with_failed_result(self, client, db_session):
        """GET returns failed status with error fields."""
        create_resp = client.post("/api/translation-tasks", json={
            "installation_id": "inst-123",
            "repository": "owner/repo",
            "base_branch": "main",
            "files": ["README.md"],
            "language": "zh-CN",
        })
        task_id = create_resp.json()["data"]["task_id"]

        import asyncio
        from app.domain.task import TaskStatus

        async def update():
            repo = TranslationTaskRepository(db_session)
            await repo.update_status(
                task_id,
                TaskStatus.FAILED,
                error_code="translation_error",
                error_message="Translation provider returned an error",
            )
        asyncio.get_event_loop().run_until_complete(update())

        response = client.get(f"/api/translation-tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "failed"
        assert data["data"]["error_code"] == "translation_error"
        assert data["data"]["error_message"] == "Translation provider returned an error"


class TestGetFilePreviews:
    """Tests for GET /api/translation-tasks/{task_id}/file-previews."""

    def test_get_file_previews_success(self, client, db_session):
        """GET returns file preview metadata for a completed task."""
        create_resp = client.post("/api/translation-tasks", json={
            "installation_id": "inst-123",
            "repository": "owner/repo",
            "base_branch": "main",
            "files": ["README.md", "docs/guide.md"],
            "language": "zh-CN",
        })
        task_id = create_resp.json()["data"]["task_id"]

        import asyncio
        from app.domain.task import TaskStatus

        async def update_task():
            repo = TranslationTaskRepository(db_session)
            await repo.update_status(
                task_id,
                TaskStatus.SUCCEEDED,
                pr_url="https://github.com/owner/repo/pull/1",
                pr_number=1,
                mappings=[
                    {"source_path": "README.md", "target_path": "README.zh-CN.md"},
                    {"source_path": "docs/guide.md", "target_path": "docs/guide.zh-CN.md"},
                ],
            )
        asyncio.get_event_loop().run_until_complete(update_task())

        response = client.get(f"/api/translation-tasks/{task_id}/file-previews")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "SUCCESS"
        assert len(data["data"]) == 2
        assert data["data"][0]["source_path"] == "README.md"
        assert data["data"][0]["target_path"] == "README.zh-CN.md"
        assert data["data"][0]["status"] == "translated"

    def test_get_file_previews_empty(self, client):
        """GET returns empty list for task with no file previews."""
        create_resp = client.post("/api/translation-tasks", json={
            "installation_id": "inst-123",
            "repository": "owner/repo",
            "base_branch": "main",
            "files": ["README.md"],
            "language": "zh-CN",
        })
        task_id = create_resp.json()["data"]["task_id"]

        response = client.get(f"/api/translation-tasks/{task_id}/file-previews")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "SUCCESS"
        assert data["data"] == []

    def test_get_file_previews_not_found(self, client):
        """GET returns 404 for unknown task_id."""
        response = client.get("/api/translation-tasks/nonexistent/file-previews")
        assert response.status_code == 404
        data = response.json()
        assert data["code"] == "TASK_NOT_FOUND"
        assert "trace_id" in data
        assert data["data"] is None


class TestInstallationVerificationPersistence:
    """Tests for installation verification with persistence."""

    def test_verify_installation_persists_metadata(self, client, db_session):
        """POST /api/github/installations/verify persists account metadata."""
        mock_result = MagicMock()
        mock_result.installation_id = 67890
        mock_result.account_login = "test-org"
        mock_result.account_type = "Organization"
        mock_result.repository_selection = "all"

        with patch("app.controller.installation_controller.get_github_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_installation.return_value = mock_result
            mock_get_client.return_value = mock_client

            response = client.post(
                "/api/github/installations/verify",
                json={"installation_id": 67890},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "SUCCESS"
        assert data["data"]["installation_id"] == 67890
        assert data["data"]["account_login"] == "test-org"

        # Verify the record was actually persisted in the database
        import asyncio

        async def check_db():
            stmt = select(InstallationAccountModel).where(
                InstallationAccountModel.installation_id == 67890
            )
            result = await db_session.execute(stmt)
            return result.scalar_one_or_none()

        record = asyncio.get_event_loop().run_until_complete(check_db())
        assert record is not None
        assert record.account_login == "test-org"
        assert record.account_type == "Organization"
