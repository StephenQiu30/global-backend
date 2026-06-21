"""Tests for InstallationService."""

from unittest.mock import MagicMock

import pytest

from app.services.github_app import InstallationInfo, RepositoryInfo


class TestInstallationServiceVerifyInstallation:
    """Test verify_installation method."""

    def test_verify_installation_success(self):
        """verify_installation returns InstallationResponse on success."""
        from app.application.installation_service import InstallationService

        mock_client = MagicMock()
        mock_client.get_installation.return_value = InstallationInfo(
            installation_id=123,
            account_login="testuser",
            account_type="User",
            repository_selection="all",
        )

        service = InstallationService(github_client=mock_client)
        result = service.verify_installation(installation_id=123)

        assert result.installation_id == 123
        assert result.account_login == "testuser"
        assert result.account_type == "User"
        assert result.repository_selection == "all"
        mock_client.get_installation.assert_called_once_with(123)

    def test_verify_installation_not_found(self):
        """verify_installation raises InstallationNotFoundError on ValueError."""
        from app.application.installation_service import (
            InstallationNotFoundError,
            InstallationService,
        )

        mock_client = MagicMock()
        mock_client.get_installation.side_effect = ValueError("not found")

        service = InstallationService(github_client=mock_client)

        with pytest.raises(InstallationNotFoundError):
            service.verify_installation(installation_id=999)

    def test_verify_installation_github_api_error(self):
        """verify_installation raises GitHubApiError on RuntimeError."""
        from app.application.installation_service import (
            GitHubApiError,
            InstallationService,
        )

        mock_client = MagicMock()
        mock_client.get_installation.side_effect = RuntimeError("API error")

        service = InstallationService(github_client=mock_client)

        with pytest.raises(GitHubApiError):
            service.verify_installation(installation_id=123)


class TestInstallationServiceListRepositories:
    """Test list_repositories method."""

    def test_list_repositories_success(self):
        """list_repositories returns RepositoryListResponse on success."""
        from app.application.installation_service import InstallationService

        mock_client = MagicMock()
        mock_client.get_installation_repos.return_value = [
            RepositoryInfo(
                full_name="owner/repo1",
                default_branch="main",
                private=False,
            ),
            RepositoryInfo(
                full_name="owner/repo2",
                default_branch="main",
                private=True,
            ),
        ]

        service = InstallationService(github_client=mock_client)
        result = service.list_repositories(installation_id=123)

        assert len(result.repositories) == 2
        assert result.repositories[0].full_name == "owner/repo1"
        assert result.repositories[0].default_branch == "main"
        assert result.repositories[0].private is False
        assert result.repositories[1].full_name == "owner/repo2"
        assert result.repositories[1].private is True
        mock_client.get_installation_repos.assert_called_once_with(123)

    def test_list_repositories_not_found(self):
        """list_repositories raises InstallationNotFoundError on ValueError."""
        from app.application.installation_service import (
            InstallationNotFoundError,
            InstallationService,
        )

        mock_client = MagicMock()
        mock_client.get_installation_repos.side_effect = ValueError("not found")

        service = InstallationService(github_client=mock_client)

        with pytest.raises(InstallationNotFoundError):
            service.list_repositories(installation_id=999)

    def test_list_repositories_github_api_error(self):
        """list_repositories raises GitHubApiError on RuntimeError."""
        from app.application.installation_service import (
            GitHubApiError,
            InstallationService,
        )

        mock_client = MagicMock()
        mock_client.get_installation_repos.side_effect = RuntimeError("API error")

        service = InstallationService(github_client=mock_client)

        with pytest.raises(GitHubApiError):
            service.list_repositories(installation_id=123)
