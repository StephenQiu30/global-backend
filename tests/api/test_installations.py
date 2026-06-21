import pytest
from unittest.mock import patch, MagicMock

from app.core.exceptions import AppException
from app.core.response import ErrorCode


def test_verify_installation_success(client):
    """POST /api/github/installations/verify returns account info on success."""
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
    assert data["message"] == "OK"
    assert "trace_id" in data
    assert data["data"]["installation_id"] == 67890
    assert data["data"]["account_login"] == "test-org"
    assert data["data"]["account_type"] == "Organization"
    assert data["data"]["repository_selection"] == "all"


def test_verify_installation_no_tokens_in_response(client):
    """Response must NOT contain any tokens or secrets."""
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

    data = response.json()
    response_str = str(data).lower()
    assert "token" not in response_str
    assert "secret" not in response_str
    assert "private_key" not in response_str
    assert "access_token" not in response_str


def test_verify_installation_not_found(client):
    """POST /api/github/installations/verify returns 404 for invalid installation."""
    with patch("app.controller.installation_controller.get_github_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_installation.side_effect = AppException(
            code=ErrorCode.INSTALLATION_NOT_FOUND,
            message="Installation not found",
            http_status=404,
        )
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/github/installations/verify",
            json={"installation_id": 99999},
        )

    assert response.status_code == 404
    data = response.json()
    assert data["code"] == "INSTALLATION_NOT_FOUND"
    assert "message" in data
    assert "trace_id" in data
    assert data["data"] is None


def test_verify_installation_github_api_error(client):
    """POST /api/github/installations/verify returns 502 on GitHub API failure."""
    with patch("app.controller.installation_controller.get_github_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_installation.side_effect = AppException(
            code=ErrorCode.GITHUB_API_ERROR,
            message="GitHub API error",
            http_status=502,
        )
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/github/installations/verify",
            json={"installation_id": 67890},
        )

    assert response.status_code == 502
    data = response.json()
    assert data["code"] == "GITHUB_API_ERROR"
    assert "message" in data
    assert "trace_id" in data
    assert data["data"] is None


def test_verify_installation_missing_body(client):
    """POST /api/github/installations/verify returns 422 for missing body."""
    response = client.post("/api/github/installations/verify")
    assert response.status_code == 422
