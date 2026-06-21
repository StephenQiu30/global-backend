"""Repository for installation account persistence."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.installation_account_model import InstallationAccountModel


class InstallationAccountRepository:
    """Data access for GitHub App installation accounts."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert(
        self,
        installation_id: int,
        account_login: str,
        account_type: str,
    ) -> InstallationAccountModel:
        """Insert or update installation account metadata."""
        stmt = select(InstallationAccountModel).where(
            InstallationAccountModel.installation_id == installation_id
        )
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing is not None:
            existing.account_login = account_login
            existing.account_type = account_type
            await self._session.commit()
            await self._session.refresh(existing)
            return existing

        model = InstallationAccountModel(
            installation_id=installation_id,
            account_login=account_login,
            account_type=account_type,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return model
