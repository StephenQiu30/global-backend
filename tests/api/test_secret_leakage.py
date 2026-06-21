"""Regression tests for secret leakage in API responses.

PRD 09: Security, Permissions, and Abuse Prevention
Spec: openspec/changes/ste-329-security-permissions/specs/secret-leakage/spec.md
"""

from unittest.mock import patch, MagicMock

import pytest

from app.core.exceptions import AppException
from app.core.response import ErrorCode
from app.services.github_app import RepositoryInfo


SENSITIVE_KEYWORDS = [
    "token",
    "secret",
    "private_key",
    "access_token",
    "OPENAI_API_KEY",
    "openai_api_key",
    "installation_token",
    "github_token",
]


class TestVerifyInstallationSecretLeakage:
    """Secret leakage tests for POST /api/github/installations/verify."""

    @pytest.mark.parametrize("keyword", SENSITIVE_KEYWORDS)
    def test_response_does_not_contain_sensitive_keyword(self, client, keyword):
        """Response body must not contain sensitive keywords."""
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

        response_str = str(response.json()).lower()
        assert keyword.lower() not in response_str, (
            f"Response contains sensitive keyword: {keyword}"
        )


class TestListRepositoriesSecretLeakage:
    """Secret leakage tests for GET /api/github/installations/{id}/repositories."""

    @pytest.mark.parametrize("keyword", SENSITIVE_KEYWORDS)
    def test_response_does_not_contain_sensitive_keyword(self, client, keyword):
        """Response body must not contain sensitive keywords."""
        mock_repos = [
            MagicMock(
                full_name="owner/repo",
                default_branch="main",
                private=True,
            )
        ]

        with patch("app.controller.installation_controller.get_github_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_installation_repos.return_value = mock_repos
            mock_get_client.return_value = mock_client

            response = client.get("/api/github/installations/12345/repositories")

        response_str = str(response.json()).lower()
        assert keyword.lower() not in response_str, (
            f"Response contains sensitive keyword: {keyword}"
        )


class TestResolveRepositorySecretLeakage:
    """Secret leakage tests for POST /api/repositories/resolve."""

    @pytest.mark.parametrize("keyword", SENSITIVE_KEYWORDS)
    def test_response_does_not_contain_sensitive_keyword(self, client, keyword):
        """Response body must not contain sensitive keywords."""
        with patch("app.controller.repository_controller.get_github_client") as mock_get_client:
            mock_client = mock_get_client.return_value
            mock_client.is_repository_authorized.return_value = True
            mock_client.get_repository_info.return_value = RepositoryInfo(
                full_name="owner/repo",
                default_branch="main",
                private=True,
            )
            response = client.post(
                "/api/repositories/resolve",
                json={"input": "owner/repo", "installation_id": 12345},
            )

        response_str = str(response.json()).lower()
        assert keyword.lower() not in response_str, (
            f"Response contains sensitive keyword: {keyword}"
        )


class TestErrorResponsesNoStackTrace:
    """Ensure error responses do not leak Python stack traces."""

    def test_404_error_no_traceback(self, client):
        """404 error response must not contain traceback."""
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

        response_str = str(response.json())
        assert "Traceback" not in response_str
        assert ".py" not in response_str

    def test_502_error_no_traceback(self, client):
        """502 error response must not contain traceback."""
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

        response_str = str(response.json())
        assert "Traceback" not in response_str
        assert ".py" not in response_str
