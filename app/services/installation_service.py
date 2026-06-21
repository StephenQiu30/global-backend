"""Application service for GitHub App installation verification."""

from app.repositories.installation_account_repository import (
    InstallationAccountRepository,
)


class InstallationService:
    """Orchestrates installation verification with persistence."""

    def __init__(
        self,
        repository: InstallationAccountRepository,
    ) -> None:
        self._repo = repository

    async def verify_and_persist(
        self,
        installation_id: int,
        account_login: str,
        account_type: str,
    ) -> dict:
        """Persist verified installation account metadata.

        Args:
            installation_id: GitHub App installation ID.
            account_login: Account login name.
            account_type: Account type (User or Organization).

        Returns:
            Dict with installation metadata.
        """
        await self._repo.upsert(
            installation_id=installation_id,
            account_login=account_login,
            account_type=account_type,
        )
        return {
            "installation_id": installation_id,
            "account_login": account_login,
            "account_type": account_type,
        }
