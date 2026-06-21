"""GitHub App client for installation, repository, and write operations."""

import base64
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import httpx
import jwt

from app.core.errors import AppError

GITHUB_API = "https://api.github.com"


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
    """Synchronous GitHub App REST client for installation and write operations."""

    def __init__(
        self,
        app_id: str,
        private_key: str,
        *,
        token_provider: Callable[[int], str] | None = None,
    ):
        self._app_id = app_id
        self._private_key = private_key
        self._token_cache: dict[int, tuple[str, float]] = {}
        self._token_provider = token_provider

    def _create_jwt(self) -> str:
        now = int(time.time())
        payload = {"iat": now - 60, "exp": now + 600, "iss": self._app_id}
        return jwt.encode(payload, self._private_key, algorithm="RS256")

    def _get_token(self, installation_id: int) -> str:
        cached = self._token_cache.get(installation_id)
        if cached and cached[1] > time.time():
            return cached[0]

        if self._token_provider:
            token = self._token_provider(installation_id)
        else:
            jwt_token = self._create_jwt()
            resp = httpx.post(
                f"{GITHUB_API}/app/installations/{installation_id}/access_tokens",
                headers={
                    "Authorization": f"Bearer {jwt_token}",
                    "Accept": "application/vnd.github+json",
                },
            )
            resp.raise_for_status()
            token = resp.json()["token"]

        expires_at = time.time() + 3000  # cache for ~50 min
        self._token_cache[installation_id] = (token, expires_at)
        return token

    def _headers(self, token: str) -> dict[str, str]:
        return {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
        }

    # --- Installation / Repository operations ---

    def get_installation(self, installation_id: int) -> InstallationInfo:
        """Get installation info by ID."""
        token = self._get_token(installation_id)
        headers = self._headers(token)

        resp = httpx.get(
            f"{GITHUB_API}/app/installations/{installation_id}",
            headers=headers,
        )
        if resp.status_code == 404:
            raise ValueError(f"Installation {installation_id} not found")
        resp.raise_for_status()

        data = resp.json()
        return InstallationInfo(
            installation_id=data["id"],
            account_login=data["account"]["login"],
            account_type=data["account"]["type"],
            repository_selection=data["repository_selection"],
        )

    def get_installation_repos(self, installation_id: int) -> list[RepositoryInfo]:
        """List repositories accessible to an installation."""
        token = self._get_token(installation_id)
        headers = self._headers(token)

        resp = httpx.get(
            f"{GITHUB_API}/installation/repositories",
            headers=headers,
        )
        if resp.status_code == 404:
            raise ValueError(f"Installation {installation_id} not found")
        resp.raise_for_status()

        data = resp.json()
        return [
            RepositoryInfo(
                full_name=repo["full_name"],
                default_branch=repo["default_branch"],
                private=repo["private"],
            )
            for repo in data.get("repositories", [])
        ]

    def is_repository_authorized(
        self, installation_id: int | str | None, full_name: str
    ) -> bool:
        """Check if a repository is authorized for an installation."""
        if installation_id is None:
            return False
        installation_id = int(installation_id)
        repos = self.get_installation_repos(installation_id)
        normalized_target = full_name.lower()
        return any(repo.full_name.lower() == normalized_target for repo in repos)

    def get_repository_info(
        self, installation_id: int | str, full_name: str
    ) -> RepositoryInfo | None:
        """Return repository metadata for an authorized installation repo."""
        installation_id = int(installation_id)
        normalized_target = full_name.lower()
        for repo in self.get_installation_repos(installation_id):
            if repo.full_name.lower() == normalized_target:
                return repo
        return None

    def get_repository_tree(
        self,
        installation_id: int | str,
        full_name: str,
        branch: str,
    ) -> list[dict[str, Any]]:
        """Fetch recursive repository tree blobs for markdown discovery."""
        installation_id = int(installation_id)
        token = self._get_token(installation_id)
        headers = self._headers(token)

        resp = httpx.get(
            f"{GITHUB_API}/repos/{full_name}/git/trees/{branch}",
            headers=headers,
            params={"recursive": "1"},
        )
        if resp.status_code == 404:
            raise ValueError(f"Repository tree not found for {full_name}@{branch}")
        resp.raise_for_status()

        return [
            {
                "path": item.get("path", ""),
                "size": item.get("size") or 0,
                "type": item.get("type", ""),
            }
            for item in resp.json().get("tree", [])
        ]

    # --- Write operations (branch, file, PR) ---

    def create_branch(
        self,
        installation_id: int,
        full_name: str,
        base_branch: str,
        branch_name: str,
    ) -> str:
        """Create a branch from the default branch SHA. Returns existing branch if 422."""
        token = self._get_token(installation_id)
        headers = self._headers(token)

        # Get default branch SHA
        ref_resp = httpx.get(
            f"{GITHUB_API}/repos/{full_name}/git/ref/heads/{base_branch}",
            headers=headers,
        )
        ref_resp.raise_for_status()
        sha = ref_resp.json()["object"]["sha"]

        # Create ref
        create_resp = httpx.post(
            f"{GITHUB_API}/repos/{full_name}/git/refs",
            headers=headers,
            json={"ref": f"refs/heads/{branch_name}", "sha": sha},
        )

        if create_resp.status_code == 422:
            # Branch already exists
            return branch_name

        create_resp.raise_for_status()
        return branch_name

    def put_file(
        self,
        installation_id: int,
        full_name: str,
        branch: str,
        path: str,
        content: str,
        message: str,
    ) -> None:
        """Write a file to the branch. Fetches SHA for existing files."""
        token = self._get_token(installation_id)
        headers = self._headers(token)
        encoded = base64.b64encode(content.encode()).decode()

        body: dict[str, Any] = {
            "message": message,
            "content": encoded,
            "branch": branch,
        }

        # Check if file exists to get SHA for update
        get_resp = httpx.get(
            f"{GITHUB_API}/repos/{full_name}/contents/{path}",
            headers=headers,
            params={"ref": branch},
        )
        if get_resp.status_code == 200:
            body["sha"] = get_resp.json()["sha"]

        put_resp = httpx.put(
            f"{GITHUB_API}/repos/{full_name}/contents/{path}",
            headers=headers,
            json=body,
        )
        put_resp.raise_for_status()

    def create_pull_request(
        self,
        installation_id: int,
        full_name: str,
        title: str,
        body: str,
        head: str,
        base: str,
    ) -> dict[str, Any]:
        """Create a PR. Returns existing PR if already open for same branch."""
        token = self._get_token(installation_id)
        headers = self._headers(token)

        create_resp = httpx.post(
            f"{GITHUB_API}/repos/{full_name}/pulls",
            headers=headers,
            json={"title": title, "body": body, "head": head, "base": base},
        )

        if create_resp.status_code == 422:
            # PR may already exist — find it
            list_resp = httpx.get(
                f"{GITHUB_API}/repos/{full_name}/pulls",
                headers=headers,
                params={"head": f"owner:{head}", "state": "open"},
            )
            list_resp.raise_for_status()
            prs = list_resp.json()
            if prs:
                return {"number": prs[0]["number"], "url": prs[0]["html_url"]}
            raise AppError("pr_create_failed", "Could not create or find PR")

        create_resp.raise_for_status()
        data = create_resp.json()
        return {"number": data["number"], "url": data["html_url"]}
