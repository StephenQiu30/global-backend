"""ORM model for translated file metadata."""

from uuid import uuid4

from sqlalchemy import DateTime, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TranslationFileModel(Base):
    """Persisted translated file preview metadata."""

    __tablename__ = "translation_files"
    __table_args__ = (
        Index("ix_translation_files_task_id", "task_id"),
    )

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True, default=lambda: uuid4().hex
    )
    task_id: Mapped[str] = mapped_column(String(36), nullable=False)
    source_path: Mapped[str] = mapped_column(String(500), nullable=False)
    target_path: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    created_at: Mapped[str] = mapped_column(
        DateTime, server_default=func.now()
    )
