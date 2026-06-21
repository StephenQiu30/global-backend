"""Tests for POST /api/public-preview endpoint."""

import pytest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import create_app
from app.services.public_repository import (
    PublicPreviewService,
    PublicPreviewResult,
    FilePreview,
    PublicRepositoryClient,
)
from app.services.translation_provider import FakeTranslationProvider


def _make_service(files_content=None):
    """Create a PublicPreviewService with mocked client."""
    mock_client = AsyncMock()
    if files_content:
        mock_client.get_file_content.side_effect = lambda o, r, b, p: files_content[p]
    else:
        mock_client.get_file_content.return_value = "# Hello World"
    provider = FakeTranslationProvider()
    return PublicPreviewService(mock_client, provider)


def _make_app(service=None):
    """Create a test app with public preview service override."""
    if service is None:
        service = _make_service()
    app = create_app(public_preview_service=service)
    return app


class TestPublicPreviewSuccess:
    """Tests for successful public preview requests."""

    def test_single_file_returns_preview(self):
        service = _make_service()
        app = _make_app(service)
        client = TestClient(app)

        response = client.post("/api/public-preview", json={
            "repository": "owner/repo",
            "files": ["README.md"],
            "language": "zh-CN",
        })

        assert response.status_code == 200
        data = response.json()
        assert len(data["previews"]) == 1
        assert data["previews"][0]["source_path"] == "README.md"
        assert data["previews"][0]["target_path"] == "README.zh-CN.md"
        assert "[zh-CN]" in data["previews"][0]["translated_content"]

    def test_multiple_files_returns_previews(self):
        service = _make_service()
        app = _make_app(service)
        client = TestClient(app)

        response = client.post("/api/public-preview", json={
            "repository": "owner/repo",
            "files": ["README.md", "docs/guide.md"],
            "language": "ja",
        })

        assert response.status_code == 200
        data = response.json()
        assert len(data["previews"]) == 2

    def test_response_has_no_pr_url(self):
        """The response must NOT contain pr_url or pr_number."""
        service = _make_service()
        app = _make_app(service)
        client = TestClient(app)

        response = client.post("/api/public-preview", json={
            "repository": "owner/repo",
            "files": ["README.md"],
            "language": "zh-CN",
        })

        assert response.status_code == 200
        data = response.json()
        assert "pr_url" not in data
        assert "pr_number" not in data


class TestPublicPreviewValidation:
    """Tests for request validation."""

    def test_empty_repository_returns_422(self):
        service = _make_service()
        app = _make_app(service)
        client = TestClient(app)

        response = client.post("/api/public-preview", json={
            "repository": "",
            "files": ["README.md"],
            "language": "zh-CN",
        })
        assert response.status_code == 422

    def test_empty_files_returns_422(self):
        service = _make_service()
        app = _make_app(service)
        client = TestClient(app)

        response = client.post("/api/public-preview", json={
            "repository": "owner/repo",
            "files": [],
            "language": "zh-CN",
        })
        assert response.status_code == 422

    def test_missing_language_returns_422(self):
        service = _make_service()
        app = _make_app(service)
        client = TestClient(app)

        response = client.post("/api/public-preview", json={
            "repository": "owner/repo",
            "files": ["README.md"],
        })
        assert response.status_code == 422


class TestPublicPreviewErrors:
    """Tests for error handling in the API."""

    def test_repository_not_found_returns_404_with_error_code(self):
        mock_client = AsyncMock()
        mock_client.get_file_content.side_effect = ValueError("repository not found")
        provider = FakeTranslationProvider()
        service = PublicPreviewService(mock_client, provider)
        app = _make_app(service)
        client = TestClient(app)

        response = client.post("/api/public-preview", json={
            "repository": "owner/nonexistent",
            "files": ["README.md"],
            "language": "zh-CN",
        })

        assert response.status_code == 404
        data = response.json()
        assert "code" in data
        assert "trace_id" in data
        assert data["data"] is None

    def test_rate_limited_returns_429_with_error_code(self):
        mock_client = AsyncMock()
        mock_client.get_file_content.side_effect = ValueError("rate_limited: GitHub API rate limit exceeded")
        provider = FakeTranslationProvider()
        service = PublicPreviewService(mock_client, provider)
        app = _make_app(service)
        client = TestClient(app)

        response = client.post("/api/public-preview", json={
            "repository": "owner/repo",
            "files": ["README.md"],
            "language": "zh-CN",
        })

        assert response.status_code == 429
        data = response.json()
        assert "code" in data
        assert "trace_id" in data
        assert data["data"] is None

    def test_unsafe_path_returns_400_with_error_code(self):
        mock_client = AsyncMock()
        provider = FakeTranslationProvider()
        service = PublicPreviewService(mock_client, provider)
        app = _make_app(service)
        client = TestClient(app)

        response = client.post("/api/public-preview", json={
            "repository": "owner/repo",
            "files": ["../../etc/passwd"],
            "language": "zh-CN",
        })

        assert response.status_code == 400
        data = response.json()
        assert "code" in data
        assert "trace_id" in data
        assert data["data"] is None

    def test_too_many_files_returns_422(self):
        mock_client = AsyncMock()
        provider = FakeTranslationProvider()
        service = PublicPreviewService(mock_client, provider)
        app = _make_app(service)
        client = TestClient(app)
        files = [f"file{i}.md" for i in range(11)]

        response = client.post("/api/public-preview", json={
            "repository": "owner/repo",
            "files": files,
            "language": "zh-CN",
        })

        assert response.status_code == 422
        data = response.json()
        assert "code" in data
        assert "trace_id" in data

    def test_translation_failure_returns_502(self):
        mock_client = AsyncMock()
        mock_client.get_file_content.return_value = "# Content"
        failing_provider = AsyncMock()
        failing_provider.translate_markdown.side_effect = RuntimeError("translation provider error")
        service = PublicPreviewService(mock_client, failing_provider)
        app = _make_app(service)
        client = TestClient(app)

        response = client.post("/api/public-preview", json={
            "repository": "owner/repo",
            "files": ["README.md"],
            "language": "zh-CN",
        })

        assert response.status_code == 502
        data = response.json()
        assert "code" in data
        assert "trace_id" in data
        assert data["data"] is None


class TestPublicPreviewNoWriteOperations:
    """Tests proving the API does not trigger GitHub writes."""

    def test_no_write_methods_called_on_client(self):
        """The preview flow must not call any write method."""
        mock_client = AsyncMock()
        mock_client.get_file_content.return_value = "# Content"
        provider = FakeTranslationProvider()
        service = PublicPreviewService(mock_client, provider)
        app = _make_app(service)
        client = TestClient(app)

        client.post("/api/public-preview", json={
            "repository": "owner/repo",
            "files": ["README.md"],
            "language": "zh-CN",
        })

        mock_client.create_branch.assert_not_called()
        mock_client.create_commit.assert_not_called()
        mock_client.create_pull.assert_not_called()
        mock_client.update_file.assert_not_called()
