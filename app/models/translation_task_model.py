"""ORM model for translation tasks."""

from uuid import uuid4

from sqlalchemy import DateTime, Index, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TranslationTaskModel(Base):
    """Persisted translation task record."""

    __tablename__ = "translation_tasks"
    __table_args__ = (
        Index("ix_translation_tasks_task_id", "task_id"),
        Index("ix_translation_tasks_installation_id", "installation_id"),
        Index("ix_translation_tasks_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True, default=lambda: uuid4().hex
    )
    task_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    installation_id: Mapped[str] = mapped_column(String(50), nullable=False)
    repository: Mapped[str] = mapped_column(String(255), nullable=False)
    base_branch: Mapped[str] = mapped_column(String(255), nullable=False)
    source_files: Mapped[list] = mapped_column(JSON, nullable=False)
    language: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="queued")
    pr_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    pr_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    file_mappings: Mapped[list | None] = mapped_column(JSON, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[str] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
