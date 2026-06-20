"""Tests for POST /api/translation-tasks endpoint."""

import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

from app.main import create_app
from app.services.translation_provider import FakeTranslationProvider
from app.services.task_runner import TaskRunner
from app.domain.task import TaskStatus, TaskResult, FileMapping


@pytest.fixture
def fake_github():
    mock = AsyncMock()
    mock.get_file_content.return_value = "# Hello World\n\nWelcome."
    return mock


@pytest.fixture
def app(fake_github):
    provider = FakeTranslationProvider()
    runner = TaskRunner(provider, fake_github)
    return create_app(task_runner=runner)


@pytest.fixture
def client(app):
    return TestClient(app)


class TestTranslationTasksSuccess:
    """Tests for successful translation task creation."""

    def test_create_task_single_file(self, client):
        response = client.post("/api/translation-tasks", json={
            "installation_id": "inst-123",
            "repository": "owner/repo",
            "base_branch": "main",
            "files": ["README.md"],
            "language": "zh-CN",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "succeeded"
        assert data["pr_url"] is not None
        assert data["pr_number"] is not None
        assert len(data["mappings"]) == 1
        assert data["mappings"][0]["source_path"] == "README.md"
        assert data["mappings"][0]["target_path"] == "README.zh-CN.md"

    def test_create_task_multiple_files(self, client):
        response = client.post("/api/translation-tasks", json={
            "installation_id": "inst-456",
            "repository": "org/project",
            "base_branch": "develop",
            "files": ["README.md", "docs/guide.md"],
            "language": "ja",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "succeeded"
        assert len(data["mappings"]) == 2


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


class TestTranslationTasksErrors:
    """Tests for task failure responses."""

    def test_file_read_error_response(self):
        fake_github = AsyncMock()
        fake_github.get_file_content.side_effect = Exception("File not found")
        provider = FakeTranslationProvider()
        runner = TaskRunner(provider, fake_github)
        app = create_app(task_runner=runner)
        client = TestClient(app)

        response = client.post("/api/translation-tasks", json={
            "installation_id": "inst-123",
            "repository": "owner/repo",
            "base_branch": "main",
            "files": ["missing.md"],
            "language": "zh-CN",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["error_code"] == "file_read_error"
        assert data["error_message"] is not None
        assert data.get("pr_url") is None

    def test_translation_error_response(self):
        fake_github = AsyncMock()
        fake_github.get_file_content.return_value = "# Content"
        failing_provider = AsyncMock()
        failing_provider.translate_markdown.side_effect = Exception("Provider error")
        runner = TaskRunner(failing_provider, fake_github)
        app = create_app(task_runner=runner)
        client = TestClient(app)

        response = client.post("/api/translation-tasks", json={
            "installation_id": "inst-123",
            "repository": "owner/repo",
            "base_branch": "main",
            "files": ["README.md"],
            "language": "zh-CN",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["error_code"] == "translation_error"
