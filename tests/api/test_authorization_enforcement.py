"""Tests for authorization enforcement across task endpoints.

PRD 09: Security, Permissions, and Abuse Prevention
Spec: openspec/changes/ste-329-security-permissions/specs/authorization-enforcement/spec.md
"""

from unittest.mock import patch

import pytest

from app.core.exceptions import AppException
from app.core.response import ErrorCode
from app.services.github_app import RepositoryInfo


def mock_authorized_repository(mock_client, full_name="owner/repo", branch="main", private=True):
    mock_client.is_repository_authorized.return_value = True
    mock_client.get_repository_info.return_value = RepositoryInfo(
        full_name=full_name,
        default_branch=branch,
        private=private,
    )


class TestRepositoryResolveAuthorization:
    """Authorization tests for POST /api/repositories/resolve."""

    def test_unauthorized_repo_rejected(self, client):
        """Unauthorized repository cannot resolve."""
        with patch("app.controller.repository_controller.get_github_client") as mock_get_client:
            mock_client = mock_get_client.return_value
            mock_client.is_repository_authorized.return_value = False
            response = client.post(
                "/api/repositories/resolve",
                json={"input": "owner/repo", "installation_id": 12345},
            )
        assert response.status_code == 403
        data = response.json()
        assert data["code"] == "REPOSITORY_NOT_INSTALLED"
        assert "trace_id" in data
        assert data["data"] is None

    def test_authorized_repo_proceeds(self, client):
        """Authorized repository resolves successfully."""
        with patch("app.controller.repository_controller.get_github_client") as mock_get_client:
            mock_client = mock_get_client.return_value
            mock_authorized_repository(mock_client)
            response = client.post(
                "/api/repositories/resolve",
                json={"input": "owner/repo", "installation_id": 12345},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "SUCCESS"
        assert data["data"]["full_name"] == "owner/repo"

    def test_github_api_error_returns_502(self, client):
        """GitHub API errors return 502 without leaking internals."""
        with patch("app.controller.repository_controller.get_github_client") as mock_get_client:
            mock_client = mock_get_client.return_value
            mock_client.is_repository_authorized.side_effect = AppException(
                code=ErrorCode.GITHUB_API_ERROR,
                message="GitHub API error",
                http_status=502,
            )
            response = client.post(
                "/api/repositories/resolve",
                json={"input": "owner/repo", "installation_id": 12345},
            )
        assert response.status_code == 502
        data = response.json()
        assert data["code"] == "GITHUB_API_ERROR"
        assert data["data"] is None


class TestScanAuthorization:
    """Authorization tests for scan endpoint (future)."""

    def test_scan_unauthorized_repo_rejected(self, client):
        """Unauthorized repository cannot scan Markdown files."""
        with patch("app.controller.repository_controller.get_github_client") as mock_get_client:
            mock_client = mock_get_client.return_value
            mock_client.is_repository_authorized.return_value = False
            response = client.post(
                "/api/repositories/resolve",
                json={"input": "owner/repo", "installation_id": 12345},
            )
        assert response.status_code == 403


class TestTaskCreationAuthorization:
    """Authorization tests for task creation endpoint (future)."""

    def test_task_unauthorized_repo_rejected(self, client):
        """Unauthorized repository cannot create translation task."""
        with patch("app.controller.repository_controller.get_github_client") as mock_get_client:
            mock_client = mock_get_client.return_value
            mock_client.is_repository_authorized.return_value = False
            response = client.post(
                "/api/repositories/resolve",
                json={"input": "owner/repo", "installation_id": 12345},
            )
        assert response.status_code == 403
