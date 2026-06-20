from dataclasses import dataclass

from github import GithubException
from github.Auth import AppAuth
from github.GithubIntegration import GithubIntegration


@dataclass
class InstallationInfo:
    installation_id: int
    account_login: str
    account_type: str
    repository_selection: str


@dataclass
class RepositoryInfo:
    full_name: str
    default_branch: str
    private: bool


class GitHubAppClient:
    def __init__(self, app_id: int, private_key: str):
        self._app_id = app_id
        self._private_key = private_key
        self._auth = AppAuth(app_id, private_key)
        self._integration = GithubIntegration(auth=self._auth)

    def get_installation(self, installation_id: int) -> InstallationInfo:
        try:
            installation = self._integration.get_app_installation(installation_id)
            return InstallationInfo(
                installation_id=installation.id,
                account_login=installation.account.login,
                account_type=installation.account.type,
                repository_selection=installation.repository_selection,
            )
        except GithubException as e:
            if e.status == 404:
                raise ValueError(f"Installation {installation_id} not found") from e
            raise RuntimeError(f"GitHub API error: {e}") from e

    def get_installation_repos(self, installation_id: int) -> list[RepositoryInfo]:
        try:
            installation = self._integration.get_app_installation(installation_id)
            repos = installation.get_repos()
            return [
                RepositoryInfo(
                    full_name=repo.full_name,
                    default_branch=repo.default_branch,
                    private=repo.private,
                )
                for repo in repos
            ]
        except GithubException as e:
            if e.status == 404:
                raise ValueError(f"Installation {installation_id} not found") from e
            raise RuntimeError(f"GitHub API error: {e}") from e
