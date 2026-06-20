import pytest
from unittest.mock import MagicMock, patch

from app.services.github_app import GitHubAppClient


@pytest.fixture
def mock_app_auth():
    with patch("app.services.github_app.AppAuth") as mock:
        yield mock


@pytest.fixture
def mock_integration():
    with patch("app.services.github_app.GithubIntegration") as mock:
        yield mock


@pytest.fixture
def client(mock_app_auth, mock_integration):
    return GitHubAppClient(app_id=12345, private_key="test-key")


def test_get_installation_returns_account_info(client, mock_integration):
    """Client must return installation account info from GitHub API."""
    mock_installation = MagicMock()
    mock_installation.id = 67890
    mock_installation.account.login = "test-org"
    mock_installation.account.type = "Organization"
    mock_installation.repository_selection = "all"

    mock_integration.return_value.get_app_installation.return_value = mock_installation

    result = client.get_installation(67890)

    assert result.installation_id == 67890
    assert result.account_login == "test-org"
    assert result.account_type == "Organization"
    assert result.repository_selection == "all"


def test_get_installation_raises_on_not_found(client, mock_integration):
    """Client must raise when installation not found."""
    from github import GithubException

    mock_integration.return_value.get_app_installation.side_effect = GithubException(
        404, "Not Found", {}
    )

    with pytest.raises(ValueError, match="not found"):
        client.get_installation(99999)


def test_get_installation_repos_returns_list(client, mock_integration):
    """Client must return list of authorized repositories."""
    mock_repo1 = MagicMock()
    mock_repo1.full_name = "org/repo1"
    mock_repo1.default_branch = "main"
    mock_repo1.private = True

    mock_repo2 = MagicMock()
    mock_repo2.full_name = "org/repo2"
    mock_repo2.default_branch = "main"
    mock_repo2.private = False

    mock_installation = MagicMock()
    mock_installation.get_repos.return_value = [mock_repo1, mock_repo2]

    mock_integration.return_value.get_app_installation.return_value = mock_installation

    result = client.get_installation_repos(67890)

    assert len(result) == 2
    assert result[0].full_name == "org/repo1"
    assert result[0].default_branch == "main"
    assert result[0].private is True
    assert result[1].full_name == "org/repo2"
    assert result[1].private is False


def test_get_installation_repos_empty_list(client, mock_integration):
    """Client must return empty list when no repos authorized."""
    mock_installation = MagicMock()
    mock_installation.get_repos.return_value = []

    mock_integration.return_value.get_app_installation.return_value = mock_installation

    result = client.get_installation_repos(67890)

    assert result == []
