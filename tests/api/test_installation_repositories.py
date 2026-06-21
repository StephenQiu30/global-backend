import pytest
from unittest.mock import patch, MagicMock

from app.core.exceptions import AppException
from app.core.response import ErrorCode


def test_list_repositories_success(client):
    """GET /api/github/installations/{id}/repositories returns repo list."""
    mock_repo = MagicMock()
    mock_repo.full_name = "org/repo1"
    mock_repo.default_branch = "main"
    mock_repo.private = True

    with patch("app.controller.installation_controller.get_github_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_installation_repos.return_value = [mock_repo]
        mock_get_client.return_value = mock_client

        response = client.get("/api/github/installations/67890/repositories")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "SUCCESS"
    assert data["message"] == "OK"
    assert "trace_id" in data
    assert "repositories" in data["data"]
    assert len(data["data"]["repositories"]) == 1
    assert data["data"]["repositories"][0]["full_name"] == "org/repo1"
    assert data["data"]["repositories"][0]["default_branch"] == "main"
    assert data["data"]["repositories"][0]["private"] is True


def test_list_repositories_empty(client):
    """GET /api/github/installations/{id}/repositories returns empty list."""
    with patch("app.controller.installation_controller.get_github_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_installation_repos.return_value = []
        mock_get_client.return_value = mock_client

        response = client.get("/api/github/installations/67890/repositories")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "SUCCESS"
    assert data["data"]["repositories"] == []


def test_list_repositories_no_tokens_in_response(client):
    """Response must NOT contain any tokens or secrets."""
    mock_repo = MagicMock()
    mock_repo.full_name = "org/repo1"
    mock_repo.default_branch = "main"
    mock_repo.private = True

    with patch("app.controller.installation_controller.get_github_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_installation_repos.return_value = [mock_repo]
        mock_get_client.return_value = mock_client

        response = client.get("/api/github/installations/67890/repositories")

    data = response.json()
    response_str = str(data).lower()
    assert "token" not in response_str
    assert "secret" not in response_str
    assert "private_key" not in response_str
    assert "access_token" not in response_str


def test_list_repositories_not_found(client):
    """GET /api/github/installations/{id}/repositories returns 404 for invalid id."""
    with patch("app.controller.installation_controller.get_github_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_installation_repos.side_effect = AppException(
            code=ErrorCode.INSTALLATION_NOT_FOUND,
            message="Installation not found",
            http_status=404,
        )
        mock_get_client.return_value = mock_client

        response = client.get("/api/github/installations/99999/repositories")

    assert response.status_code == 404
    data = response.json()
    assert data["code"] == "INSTALLATION_NOT_FOUND"
    assert data["data"] is None


def test_list_repositories_github_api_error(client):
    """GET /api/github/installations/{id}/repositories returns 502 on GitHub failure."""
    with patch("app.controller.installation_controller.get_github_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_installation_repos.side_effect = AppException(
            code=ErrorCode.GITHUB_API_ERROR,
            message="GitHub API error",
            http_status=502,
        )
        mock_get_client.return_value = mock_client

        response = client.get("/api/github/installations/67890/repositories")

    assert response.status_code == 502
    data = response.json()
    assert data["code"] == "GITHUB_API_ERROR"
    assert data["data"] is None
