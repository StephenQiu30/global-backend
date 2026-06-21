"""Application service for GitHub installation operations."""

from pydantic import BaseModel

from app.services.github_app import GitHubAppClient


class InstallationNotFoundError(Exception):
    """Raised when a GitHub installation is not found."""

    pass


class GitHubApiError(Exception):
    """Raised when GitHub API returns an error."""

    pass


class InstallationResponse(BaseModel):
    """Response DTO for installation verification."""

    installation_id: int
    account_login: str
    account_type: str
    repository_selection: str


class RepositoryItem(BaseModel):
    """DTO for a single repository."""

    full_name: str
    default_branch: str
    private: bool


class RepositoryListResponse(BaseModel):
    """Response DTO for repository listing."""

    repositories: list[RepositoryItem]


class InstallationService:
    """Service for GitHub installation verification and repository listing.

    Args:
        github_client: GitHub App client for API operations.
    """

    def __init__(self, github_client: GitHubAppClient) -> None:
        self._client = github_client

    def verify_installation(self, installation_id: int) -> InstallationResponse:
        """Verify a GitHub installation and return its metadata.

        Args:
            installation_id: The GitHub installation ID.

        Returns:
            InstallationResponse with account metadata.

        Raises:
            InstallationNotFoundError: If installation does not exist.
            GitHubApiError: If GitHub API call fails.
        """
        try:
            info = self._client.get_installation(installation_id)
            return InstallationResponse(
                installation_id=info.installation_id,
                account_login=info.account_login,
                account_type=info.account_type,
                repository_selection=info.repository_selection,
            )
        except ValueError:
            raise InstallationNotFoundError(
                f"Installation {installation_id} not found"
            )
        except RuntimeError:
            raise GitHubApiError("GitHub API error")

    def list_repositories(self, installation_id: int) -> RepositoryListResponse:
        """List repositories accessible to an installation.

        Args:
            installation_id: The GitHub installation ID.

        Returns:
            RepositoryListResponse with repository list.

        Raises:
            InstallationNotFoundError: If installation does not exist.
            GitHubApiError: If GitHub API call fails.
        """
        try:
            repos = self._client.get_installation_repos(installation_id)
            return RepositoryListResponse(
                repositories=[
                    RepositoryItem(
                        full_name=r.full_name,
                        default_branch=r.default_branch,
                        private=r.private,
                    )
                    for r in repos
                ]
            )
        except ValueError:
            raise InstallationNotFoundError(
                f"Installation {installation_id} not found"
            )
        except RuntimeError:
            raise GitHubApiError("GitHub API error")
