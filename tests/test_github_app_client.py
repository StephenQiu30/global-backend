import httpx
import pytest
import respx

from app.services.github_app import GitHubAppClient


@pytest.fixture
def client():
    return GitHubAppClient(
        app_id="12345",
        private_key="test-key",
        token_provider=lambda _installation_id: "installation-token",
    )


@respx.mock
def test_get_installation_returns_account_info(client):
    """Client must return installation account info from GitHub API."""
    respx.get("https://api.github.com/app/installations/67890").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": 67890,
                "account": {"login": "test-org", "type": "Organization"},
                "repository_selection": "all",
            },
        )
    )

    result = client.get_installation(67890)

    assert result.installation_id == 67890
    assert result.account_login == "test-org"
    assert result.account_type == "Organization"
    assert result.repository_selection == "all"


@respx.mock
def test_get_installation_raises_on_not_found(client):
    """Client must raise when installation not found."""
    respx.get("https://api.github.com/app/installations/99999").mock(
        return_value=httpx.Response(404, json={"message": "Not Found"})
    )

    with pytest.raises(ValueError, match="not found"):
        client.get_installation(99999)


@respx.mock
def test_get_installation_repos_returns_list(client):
    """Client must return list of authorized repositories."""
    respx.get("https://api.github.com/installation/repositories").mock(
        return_value=httpx.Response(
            200,
            json={
                "repositories": [
                    {
                        "full_name": "org/repo1",
                        "default_branch": "main",
                        "private": True,
                    },
                    {
                        "full_name": "org/repo2",
                        "default_branch": "main",
                        "private": False,
                    },
                ]
            },
        )
    )

    result = client.get_installation_repos(67890)

    assert len(result) == 2
    assert result[0].full_name == "org/repo1"
    assert result[0].default_branch == "main"
    assert result[0].private is True
    assert result[1].full_name == "org/repo2"
    assert result[1].private is False


@respx.mock
def test_get_installation_repos_empty_list(client):
    """Client must return empty list when no repos authorized."""
    respx.get("https://api.github.com/installation/repositories").mock(
        return_value=httpx.Response(200, json={"repositories": []})
    )

    result = client.get_installation_repos(67890)

    assert result == []
