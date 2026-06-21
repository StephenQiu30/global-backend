"""Tests for Markdown files API endpoint."""

import asyncio
import pytest
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

from app.controller.repository_controller import router
from app.services.markdown_discovery import MarkdownFileInfo


@pytest.fixture
def client():
    """Create test client."""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router, prefix="/api")
    return TestClient(app)


@pytest.fixture(autouse=True)
def mock_github_client():
    """Mock GitHub client for all tests."""
    mock_client = MagicMock()
    mock_client.is_repository_authorized.return_value = True
    mock_client.get_repository_info.return_value = MagicMock(
        default_branch="main",
        private=True,
        full_name="test-owner/test-repo",
    )
    mock_client.get_repository_tree.return_value = []
    with patch("app.controller.repository_controller.get_github_client") as mock_func:
        mock_func.return_value = mock_client
        yield mock_client
        mock_func.reset_mock()


class TestGetMarkdownFiles:
    """Test GET /api/repositories/{owner}/{repo}/markdown-files endpoint."""

    def test_missing_installation_id(self, client, mock_github_client):
        """GIVEN no installation_id THEN returns 404 repository_not_installed."""
        response = client.get("/api/repositories/test-owner/test-repo/markdown-files")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"] == "repository_not_installed"
        mock_github_client.is_repository_authorized.assert_not_called()

    @patch("app.controller.repository_controller.discover_markdown_files")
    def test_empty_repository(self, mock_discover, client):
        """GIVEN authorized repo with no markdown files THEN returns empty list."""
        mock_discover.return_value = []

        response = client.get(
            "/api/repositories/test-owner/test-repo/markdown-files",
            params={"installation_id": "12345"}
        )

        assert response.status_code == 200
        assert response.json() == []

    @patch("app.controller.repository_controller.discover_markdown_files")
    def test_returns_markdown_files(self, mock_discover, client):
        """GIVEN authorized repo with markdown files THEN returns file list."""
        mock_discover.return_value = [
            MarkdownFileInfo(
                path="README.md",
                size_bytes=1024,
                is_default_readme=True,
                is_translated_variant=False,
                disabled_reason=None,
                target_path_preview="README.zh-CN.md",
                target_exists=False,
            ),
            MarkdownFileInfo(
                path="docs/guide.md",
                size_bytes=2048,
                is_default_readme=False,
                is_translated_variant=False,
                disabled_reason=None,
                target_path_preview="docs/guide.zh-CN.md",
                target_exists=False,
            ),
        ]

        response = client.get(
            "/api/repositories/test-owner/test-repo/markdown-files",
            params={"installation_id": "12345"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["path"] == "README.md"
        assert data[0]["is_default_readme"] is True
        assert data[1]["path"] == "docs/guide.md"

    @patch("app.controller.repository_controller.discover_markdown_files")
    def test_custom_language_parameter(self, mock_discover, client):
        """GIVEN language=ja THEN target paths use ja suffix."""
        mock_discover.return_value = [
            MarkdownFileInfo(
                path="README.md",
                size_bytes=1024,
                is_default_readme=True,
                is_translated_variant=False,
                disabled_reason=None,
                target_path_preview="README.ja.md",
                target_exists=False,
            ),
        ]

        response = client.get(
            "/api/repositories/test-owner/test-repo/markdown-files",
            params={"installation_id": "12345", "language": "ja"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data[0]["target_path_preview"] == "README.ja.md"

    @patch("app.controller.repository_controller.discover_markdown_files")
    def test_default_language_is_zh_cn(self, mock_discover, client):
        """GIVEN no language parameter THEN defaults to zh-CN."""
        mock_discover.return_value = [
            MarkdownFileInfo(
                path="README.md",
                size_bytes=1024,
                is_default_readme=True,
                is_translated_variant=False,
                disabled_reason=None,
                target_path_preview="README.zh-CN.md",
                target_exists=False,
            ),
        ]

        response = client.get(
            "/api/repositories/test-owner/test-repo/markdown-files",
            params={"installation_id": "12345"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data[0]["target_path_preview"] == "README.zh-CN.md"

    @patch("app.controller.repository_controller.discover_markdown_files")
    def test_includes_disabled_reason(self, mock_discover, client):
        """GIVEN oversized file THEN response includes disabled_reason."""
        mock_discover.return_value = [
            MarkdownFileInfo(
                path="large.md",
                size_bytes=300 * 1024,
                is_default_readme=False,
                is_translated_variant=False,
                disabled_reason="File size (307200 bytes) exceeds maximum (204800 bytes)",
                target_path_preview="large.zh-CN.md",
                target_exists=False,
            ),
        ]

        # Note: This file exceeds MAX_TOTAL_SIZE, so validate_selection will return error
        # The endpoint now calls validate_selection, so this will return 400
        response = client.get(
            "/api/repositories/test-owner/test-repo/markdown-files",
            params={"installation_id": "12345"}
        )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "selection_limit_exceeded"

    @patch("app.controller.repository_controller.discover_markdown_files")
    def test_response_format(self, mock_discover, client):
        """GIVEN file list THEN response has correct structure."""
        mock_discover.return_value = [
            MarkdownFileInfo(
                path="README.md",
                size_bytes=1024,
                is_default_readme=True,
                is_translated_variant=False,
                disabled_reason=None,
                target_path_preview="README.zh-CN.md",
                target_exists=False,
            ),
        ]

        response = client.get(
            "/api/repositories/test-owner/test-repo/markdown-files",
            params={"installation_id": "12345"}
        )

        assert response.status_code == 200
        data = response.json()
        file = data[0]

        # Check all required fields are present
        assert "path" in file
        assert "size_bytes" in file
        assert "is_default_readme" in file
        assert "is_translated_variant" in file
        assert "disabled_reason" in file
        assert "target_path_preview" in file
        assert "target_exists" in file

    @patch("app.controller.repository_controller.discover_markdown_files")
    def test_validate_selection_called(self, mock_discover, client):
        """GIVEN files exceeding limits THEN returns 400 selection_limit_exceeded."""
        # Create 11 files to exceed MAX_FILE_COUNT (10)
        mock_discover.return_value = [
            MarkdownFileInfo(
                path=f"file{i}.md",
                size_bytes=1024,
                is_default_readme=False,
                is_translated_variant=False,
                disabled_reason=None,
                target_path_preview=f"file{i}.zh-CN.md",
                target_exists=False,
            )
            for i in range(11)
        ]

        response = client.get(
            "/api/repositories/test-owner/test-repo/markdown-files",
            params={"installation_id": "12345"}
        )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "selection_limit_exceeded"
        assert "file count" in data["detail"]["message"].lower()
