"""ORM model for GitHub App installation accounts."""

from uuid import uuid4

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class InstallationAccountModel(Base):
    """Persisted GitHub App installation account metadata."""

    __tablename__ = "installation_accounts"

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True, default=lambda: uuid4().hex
    )
    installation_id: Mapped[int] = mapped_column(
        Integer, unique=True, nullable=False
    )
    account_login: Mapped[str] = mapped_column(String(255), nullable=False)
    account_type: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[str] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
