from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestRepositoryResolve:
    """Tests for POST /api/repositories/resolve endpoint."""

    def test_resolve_authorized_repository(self, client):
        """Resolve authorized repository successfully."""
        with patch(
            "app.api.repositories.github_service.is_repository_authorized",
            new_callable=AsyncMock,
            return_value=True,
        ):
            response = client.post(
                "/api/repositories/resolve",
                json={"input": "owner/repo", "installation_id": 12345},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["full_name"] == "owner/repo"
            assert "default_branch" in data
            assert "private" in data

    def test_resolve_unauthorized_repository(self, client):
        """Reject unauthorized repository."""
        with patch(
            "app.api.repositories.github_service.is_repository_authorized",
            new_callable=AsyncMock,
            return_value=False,
        ):
            response = client.post(
                "/api/repositories/resolve",
                json={"input": "owner/repo", "installation_id": 12345},
            )
            assert response.status_code == 403
            data = response.json()
            assert data["detail"]["error"] == "repository_not_installed"

    def test_resolve_invalid_url(self, client):
        """Reject invalid repository URL."""
        response = client.post(
            "/api/repositories/resolve",
            json={"input": "https://gitlab.com/owner/repo", "installation_id": 12345},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "invalid_repository_url"

    def test_resolve_empty_input(self, client):
        """Reject empty input."""
        response = client.post(
            "/api/repositories/resolve",
            json={"input": "", "installation_id": 12345},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "invalid_repository_url"

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
            "app.api.repositories.github_service.is_repository_authorized",
            new_callable=AsyncMock,
            return_value=True,
        ):
            response = client.post(
                "/api/repositories/resolve",
                json={"input": "https://github.com/owner/repo", "installation_id": 12345},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["full_name"] == "owner/repo"

    def test_resolve_ssh_url_rejected(self, client):
        """Reject SSH URL."""
        response = client.post(
            "/api/repositories/resolve",
            json={"input": "git@github.com:owner/repo.git", "installation_id": 12345},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "invalid_repository_url"
