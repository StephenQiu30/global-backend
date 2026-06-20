from unittest.mock import AsyncMock, patch

import pytest

from app.services.github_app import GithubAppService


@pytest.fixture
def github_service():
    """Create GithubAppService instance for testing."""
    return GithubAppService()


class TestGithubAppService:
    """Tests for GithubAppService."""

    @pytest.mark.asyncio
    async def test_get_installation_repositories(self, github_service):
        """Get repositories for an installation."""
        mock_response = {
            "repositories": [
                {
                    "full_name": "owner/repo1",
                    "default_branch": "main",
                    "private": True,
                },
                {
                    "full_name": "owner/repo2",
                    "default_branch": "master",
                    "private": False,
                },
            ]
        }
        with patch.object(
            github_service, "_make_request", new_callable=AsyncMock, return_value=mock_response
        ):
            repos = await github_service.get_installation_repositories(installation_id=12345)
            assert len(repos) == 2
            assert repos[0]["full_name"] == "owner/repo1"
            assert repos[1]["full_name"] == "owner/repo2"

    @pytest.mark.asyncio
    async def test_is_repository_authorized_true(self, github_service):
        """Return True for authorized repository."""
        mock_repos = [
            {"full_name": "owner/repo1", "default_branch": "main", "private": True},
        ]
        with patch.object(
            github_service, "get_installation_repositories", new_callable=AsyncMock, return_value=mock_repos
        ):
            result = await github_service.is_repository_authorized(
                installation_id=12345, full_name="owner/repo1"
            )
            assert result is True

    @pytest.mark.asyncio
    async def test_is_repository_authorized_false(self, github_service):
        """Return False for unauthorized repository."""
        mock_repos = [
            {"full_name": "owner/repo1", "default_branch": "main", "private": True},
        ]
        with patch.object(
            github_service, "get_installation_repositories", new_callable=AsyncMock, return_value=mock_repos
        ):
            result = await github_service.is_repository_authorized(
                installation_id=12345, full_name="owner/repo2"
            )
            assert result is False

    @pytest.mark.asyncio
    async def test_is_repository_authorized_case_insensitive(self, github_service):
        """Authorization check is case-insensitive."""
        mock_repos = [
            {"full_name": "owner/repo1", "default_branch": "main", "private": True},
        ]
        with patch.object(
            github_service, "get_installation_repositories", new_callable=AsyncMock, return_value=mock_repos
        ):
            result = await github_service.is_repository_authorized(
                installation_id=12345, full_name="Owner/Repo1"
            )
            assert result is True
