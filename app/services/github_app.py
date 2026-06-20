from typing import Any

import httpx


class GithubAppService:
    """Service for interacting with GitHub App API."""

    GITHUB_API_BASE = "https://api.github.com"

    async def get_installation_repositories(
        self, installation_id: int
    ) -> list[dict[str, Any]]:
        """Get repositories authorized for an installation."""
        response = await self._make_request(
            "GET",
            f"/installation/repositories",
            installation_id=installation_id,
        )
        return response.get("repositories", [])

    async def is_repository_authorized(
        self, installation_id: int, full_name: str
    ) -> bool:
        """Check if a repository is authorized for an installation."""
        repos = await self.get_installation_repositories(installation_id)
        normalized_target = full_name.lower()
        return any(repo["full_name"].lower() == normalized_target for repo in repos)

    async def _make_request(
        self,
        method: str,
        path: str,
        installation_id: int,
    ) -> dict[str, Any]:
        """Make an authenticated request to GitHub API.

        In production, this would create a JWT and installation token.
        For testing, this method is mocked.
        """
        # This is a placeholder - real implementation would use JWT auth
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{self.GITHUB_API_BASE}{path}",
                headers={
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )
            response.raise_for_status()
            return response.json()
