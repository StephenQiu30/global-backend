from unittest.mock import MagicMock, patch

import pytest

from app.services.github_app import GitHubAppClient


@pytest.fixture
def github_client():
    """Create GitHubAppClient instance for testing."""
    with patch("app.services.github_app.AppAuth"), patch(
        "app.services.github_app.GithubIntegration"
    ):
        return GitHubAppClient(app_id=12345, private_key="fake-key")


class TestGitHubAppClient:
    """Tests for GitHubAppClient."""

    def test_get_installation_repositories(self, github_client):
        """Get repositories for an installation."""
        mock_repo1 = MagicMock()
        mock_repo1.full_name = "owner/repo1"
        mock_repo1.default_branch = "main"
        mock_repo1.private = True

        mock_repo2 = MagicMock()
        mock_repo2.full_name = "owner/repo2"
        mock_repo2.default_branch = "master"
        mock_repo2.private = False

        mock_installation = MagicMock()
        mock_installation.get_repos.return_value = [mock_repo1, mock_repo2]

        github_client._integration.get_app_installation.return_value = (
            mock_installation
        )

        repos = github_client.get_installation_repos(installation_id=12345)
        assert len(repos) == 2
        assert repos[0].full_name == "owner/repo1"
        assert repos[1].full_name == "owner/repo2"

    def test_is_repository_authorized_true(self, github_client):
        """Return True for authorized repository."""
        mock_repo = MagicMock()
        mock_repo.full_name = "owner/repo1"
        mock_repo.default_branch = "main"
        mock_repo.private = True

        mock_installation = MagicMock()
        mock_installation.get_repos.return_value = [mock_repo]
        github_client._integration.get_app_installation.return_value = (
            mock_installation
        )

        result = github_client.is_repository_authorized(
            installation_id=12345, full_name="owner/repo1"
        )
        assert result is True

    def test_is_repository_authorized_false(self, github_client):
        """Return False for unauthorized repository."""
        mock_repo = MagicMock()
        mock_repo.full_name = "owner/repo1"
        mock_repo.default_branch = "main"
        mock_repo.private = True

        mock_installation = MagicMock()
        mock_installation.get_repos.return_value = [mock_repo]
        github_client._integration.get_app_installation.return_value = (
            mock_installation
        )

        result = github_client.is_repository_authorized(
            installation_id=12345, full_name="owner/repo2"
        )
        assert result is False

    def test_is_repository_authorized_case_insensitive(self, github_client):
        """Authorization check is case-insensitive."""
        mock_repo = MagicMock()
        mock_repo.full_name = "owner/repo1"
        mock_repo.default_branch = "main"
        mock_repo.private = True

        mock_installation = MagicMock()
        mock_installation.get_repos.return_value = [mock_repo]
        github_client._integration.get_app_installation.return_value = (
            mock_installation
        )

        result = github_client.is_repository_authorized(
            installation_id=12345, full_name="Owner/Repo1"
        )
        assert result is True
