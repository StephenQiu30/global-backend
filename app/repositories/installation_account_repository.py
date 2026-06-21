"""Repository for installation account persistence."""

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.installation_account import InstallationAccountModel


@dataclass
class InstallationAccountData:
    """Domain data for an installation account (VO-friendly)."""

    installation_id: int
    account_login: str
    account_type: str
    repository_selection: str


def _model_to_data(model: InstallationAccountModel) -> InstallationAccountData:
    """Convert ORM model to domain data.

    Args:
        model: ORM model instance

    Returns:
        Domain data instance
    """
    return InstallationAccountData(
        installation_id=model.installation_id,
        account_login=model.account_login,
        account_type=model.account_type,
        repository_selection=model.repository_selection,
    )


class InstallationAccountRepository:
    """Repository for installation account persistence.

    Args:
        session: Async SQLAlchemy session
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert(
        self,
        installation_id: int,
        account_login: str,
        account_type: str,
        repository_selection: str,
    ) -> InstallationAccountData:
        """Upsert an installation account.

        Creates a new record if installation_id doesn't exist,
        updates existing record otherwise.

        Args:
            installation_id: GitHub App installation ID
            account_login: Account login name
            account_type: Account type (User or Organization)
            repository_selection: Repository selection (all or selected)

        Returns:
            Saved installation account data
        """
        stmt = select(InstallationAccountModel).where(
            InstallationAccountModel.installation_id == installation_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            # Create new
            model = InstallationAccountModel(
                installation_id=installation_id,
                account_login=account_login,
                account_type=account_type,
                repository_selection=repository_selection,
            )
            self._session.add(model)
        else:
            # Update existing
            model.account_login = account_login
            model.account_type = account_type
            model.repository_selection = repository_selection

        await self._session.flush()
        await self._session.refresh(model)
        return _model_to_data(model)

    async def get_by_installation_id(
        self, installation_id: int
    ) -> Optional[InstallationAccountData]:
        """Get an installation account by installation ID.

        Args:
            installation_id: GitHub App installation ID

        Returns:
            Installation account data if found, None otherwise
        """
        stmt = select(InstallationAccountModel).where(
            InstallationAccountModel.installation_id == installation_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return _model_to_data(model)
