from unittest.mock import patch

import pytest

from app.services.github_app import RepositoryInfo


def mock_authorized_repository(mock_client, full_name="owner/repo", branch="main", private=True):
    mock_client.is_repository_authorized.return_value = True
    mock_client.get_repository_info.return_value = RepositoryInfo(
        full_name=full_name,
        default_branch=branch,
        private=private,
    )


class TestRepositoryResolve:
    """Tests for POST /api/repositories/resolve endpoint."""

    def test_resolve_authorized_repository(self, client):
        """Resolve authorized repository successfully."""
        with patch(
            "app.controller.repository_controller.get_github_client"
        ) as mock_get_client:
            mock_client = mock_get_client.return_value
            mock_authorized_repository(mock_client)
            response = client.post(
                "/api/repositories/resolve",
                json={"input": "owner/repo", "installation_id": 12345},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == "SUCCESS"
            assert data["message"] == "OK"
            assert "trace_id" in data
            assert data["data"]["full_name"] == "owner/repo"
            assert "default_branch" in data["data"]
            assert "private" in data["data"]

    def test_resolve_unauthorized_repository(self, client):
        """Reject unauthorized repository."""
        with patch(
            "app.controller.repository_controller.get_github_client"
        ) as mock_get_client:
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

    def test_resolve_invalid_url(self, client):
        """Reject invalid repository URL."""
        response = client.post(
            "/api/repositories/resolve",
            json={"input": "https://gitlab.com/owner/repo", "installation_id": 12345},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["code"] == "VALIDATION_ERROR"
        assert "trace_id" in data
        assert data["data"] is None

    def test_resolve_empty_input(self, client):
        """Reject empty input."""
        response = client.post(
            "/api/repositories/resolve",
            json={"input": "", "installation_id": 12345},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["code"] == "VALIDATION_ERROR"
        assert "trace_id" in data
        assert data["data"] is None

    def test_resolve_missing_installation_id(self, client):
        """Reject missing installation_id."""
        response = client.post(
            "/api/repositories/resolve",
            json={"input": "owner/repo"},
        )
        assert response.status_code == 422

    def test_resolve_full_https_url(self, client):
        """Resolve full HTTPS URL."""
        with patch(
            "app.controller.repository_controller.get_github_client"
        ) as mock_get_client:
            mock_client = mock_get_client.return_value
            mock_authorized_repository(mock_client)
            response = client.post(
                "/api/repositories/resolve",
                json={"input": "https://github.com/owner/repo", "installation_id": 12345},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["data"]["full_name"] == "owner/repo"

    def test_resolve_ssh_url_rejected(self, client):
        """Reject SSH URL."""
        response = client.post(
            "/api/repositories/resolve",
            json={"input": "git@github.com:owner/repo.git", "installation_id": 12345},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["code"] == "VALIDATION_ERROR"
        assert "trace_id" in data
