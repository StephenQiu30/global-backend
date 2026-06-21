import httpx
import pytest
import respx

from app.services.github_app import GitHubAppClient


@pytest.fixture
def github_client():
    return GitHubAppClient(
        app_id="12345",
        private_key="fake-key",
        token_provider=lambda _installation_id: "installation-token",
    )


class TestGitHubAppClient:
    """Tests for GitHubAppClient repository authorization."""

    @respx.mock
    def test_get_installation_repositories(self, github_client):
        """Get repositories for an installation."""
        respx.get("https://api.github.com/installation/repositories").mock(
            return_value=httpx.Response(
                200,
                json={
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
                },
            )
        )

        repos = github_client.get_installation_repos(installation_id=12345)
        assert len(repos) == 2
        assert repos[0].full_name == "owner/repo1"
        assert repos[1].full_name == "owner/repo2"

    @respx.mock
    def test_is_repository_authorized_true(self, github_client):
        """Return True for authorized repository."""
        respx.get("https://api.github.com/installation/repositories").mock(
            return_value=httpx.Response(
                200,
                json={
                    "repositories": [
                        {
                            "full_name": "owner/repo1",
                            "default_branch": "main",
                            "private": True,
                        }
                    ]
                },
            )
        )

        result = github_client.is_repository_authorized(
            installation_id=12345, full_name="owner/repo1"
        )
        assert result is True

    @respx.mock
    def test_is_repository_authorized_false(self, github_client):
        """Return False for unauthorized repository."""
        respx.get("https://api.github.com/installation/repositories").mock(
            return_value=httpx.Response(
                200,
                json={
                    "repositories": [
                        {
                            "full_name": "owner/repo1",
                            "default_branch": "main",
                            "private": True,
                        }
                    ]
                },
            )
        )

        result = github_client.is_repository_authorized(
            installation_id=12345, full_name="owner/repo2"
        )
        assert result is False

    @respx.mock
    def test_is_repository_authorized_case_insensitive(self, github_client):
        """Authorization check is case-insensitive."""
        respx.get("https://api.github.com/installation/repositories").mock(
            return_value=httpx.Response(
                200,
                json={
                    "repositories": [
                        {
                            "full_name": "owner/repo1",
                            "default_branch": "main",
                            "private": True,
                        }
                    ]
                },
            )
        )

        result = github_client.is_repository_authorized(
            installation_id=12345, full_name="Owner/Repo1"
        )
        assert result is True


class TestGitHubRepositoryTree:
    @respx.mock
    def test_get_repository_tree_returns_blobs(self, github_client):
        respx.get(
            "https://api.github.com/repos/owner/repo/git/trees/main",
            params={"recursive": "1"},
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "tree": [
                        {"path": "README.md", "type": "blob", "size": 100},
                        {"path": "docs", "type": "tree"},
                    ]
                },
            )
        )

        items = github_client.get_repository_tree(12345, "owner/repo", "main")

        assert items == [
            {"path": "README.md", "size": 100, "type": "blob"},
            {"path": "docs", "size": 0, "type": "tree"},
        ]

    @respx.mock
    def test_get_repository_tree_not_found(self, github_client):
        respx.get("https://api.github.com/repos/owner/repo/git/trees/main").mock(
            return_value=httpx.Response(404, json={"message": "Not Found"})
        )

        with pytest.raises(ValueError, match="not found"):
            github_client.get_repository_tree(12345, "owner/repo", "main")
