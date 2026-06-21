"""Tests for TranslationTaskRepository and InstallationAccountRepository.

TDD Red phase: these tests define expected repository behavior.
They should fail until the repository implementations are created.
"""

import json
import uuid

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.models.base import Base
from app.domain.task import TaskStatus
from app.repositories.installation_account_repository import InstallationAccountRepository
from app.repositories.translation_task_repository import TranslationTaskRepository


@pytest_asyncio.fixture
async def session():
    """Provide an async database session with tables created per test."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as sess:
        yield sess

    await engine.dispose()


@pytest.fixture
def task_repo(session: AsyncSession) -> TranslationTaskRepository:
    return TranslationTaskRepository(session)


@pytest.fixture
def account_repo(session: AsyncSession) -> InstallationAccountRepository:
    return InstallationAccountRepository(session)


# --- TranslationTaskRepository ---


class TestTranslationTaskRepository:
    """Tests for TranslationTaskRepository CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_queued_task(self, task_repo: TranslationTaskRepository):
        """Repository.create returns a task with QUEUED status and a UUID task_id."""
        result = await task_repo.create(
            installation_id="12345",
            repository="acme/docs",
            base_branch="main",
            files=["README.md", "guide.md"],
            language="ja",
        )

        assert result.status == TaskStatus.QUEUED
        assert result.installation_id == "12345"
        assert result.repository == "acme/docs"
        assert result.files == ["README.md", "guide.md"]
        assert result.language == "ja"
        # task_id should be a valid UUID string
        uuid.UUID(result.task_id)

    @pytest.mark.asyncio
    async def test_create_task_is_persisted(self, task_repo: TranslationTaskRepository):
        """A created task can be retrieved by its task_id."""
        created = await task_repo.create(
            installation_id="100",
            repository="org/repo",
            base_branch="main",
            files=["index.md"],
            language="ko",
        )

        fetched = await task_repo.get_by_id(created.task_id)

        assert fetched is not None
        assert fetched.task_id == created.task_id
        assert fetched.status == TaskStatus.QUEUED

    @pytest.mark.asyncio
    async def test_update_status_to_running(self, task_repo: TranslationTaskRepository):
        """update_status transitions a queued task to running."""
        task = await task_repo.create(
            installation_id="1",
            repository="o/r",
            base_branch="main",
            files=["a.md"],
            language="zh-CN",
        )

        result = await task_repo.update_status(task.task_id, TaskStatus.RUNNING)

        assert result is not None
        assert result.status == TaskStatus.RUNNING

    @pytest.mark.asyncio
    async def test_update_status_to_succeeded(self, task_repo: TranslationTaskRepository):
        """update_status with succeeded stores PR info and file mappings."""
        task = await task_repo.create(
            installation_id="1",
            repository="o/r",
            base_branch="main",
            files=["a.md"],
            language="es",
        )
        await task_repo.update_status(task.task_id, TaskStatus.RUNNING)

        result = await task_repo.update_status(
            task.task_id,
            TaskStatus.SUCCEEDED,
            pr_url="https://github.com/o/r/pull/42",
            pr_number=42,
            mappings=[{"source_path": "a.md", "target_path": "i18n/es/a.md"}],
        )

        assert result is not None
        assert result.status == TaskStatus.SUCCEEDED
        assert result.pr_url == "https://github.com/o/r/pull/42"
        assert result.pr_number == 42
        assert result.mappings == [{"source_path": "a.md", "target_path": "i18n/es/a.md"}]

    @pytest.mark.asyncio
    async def test_update_status_to_failed(self, task_repo: TranslationTaskRepository):
        """update_status with failed stores safe error code and message."""
        task = await task_repo.create(
            installation_id="1",
            repository="o/r",
            base_branch="main",
            files=["a.md"],
            language="fr",
        )
        await task_repo.update_status(task.task_id, TaskStatus.RUNNING)

        result = await task_repo.update_status(
            task.task_id,
            TaskStatus.FAILED,
            error_code="translation_error",
            error_message="Translation provider returned an error",
        )

        assert result is not None
        assert result.status == TaskStatus.FAILED
        assert result.error_code == "translation_error"
        assert result.error_message == "Translation provider returned an error"

    @pytest.mark.asyncio
    async def test_update_status_nonexistent_returns_none(
        self, task_repo: TranslationTaskRepository
    ):
        """update_status returns None when task_id does not exist."""
        result = await task_repo.update_status(
            "nonexistent-id", TaskStatus.RUNNING,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_id_nonexistent(self, task_repo: TranslationTaskRepository):
        """get_by_id returns None for a non-existent task."""
        result = await task_repo.get_by_id("nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_file_previews_for_succeeded_task(
        self, task_repo: TranslationTaskRepository
    ):
        """get_file_previews returns file mappings for a succeeded task."""
        task = await task_repo.create(
            installation_id="1",
            repository="o/r",
            base_branch="main",
            files=["a.md", "b.md"],
            language="ja",
        )
        mappings = [
            {"source_path": "a.md", "target_path": "i18n/ja/a.md"},
            {"source_path": "b.md", "target_path": "i18n/ja/b.md"},
        ]
        await task_repo.update_status(
            task.task_id,
            TaskStatus.SUCCEEDED,
            pr_url="https://github.com/o/r/pull/1",
            pr_number=1,
            mappings=mappings,
        )

        previews = await task_repo.get_file_previews(task.task_id)

        assert len(previews) == 2
        assert previews[0]["source_path"] == "a.md"
        assert previews[1]["target_path"] == "i18n/ja/b.md"

    @pytest.mark.asyncio
    async def test_get_file_previews_for_non_succeeded_task(
        self, task_repo: TranslationTaskRepository
    ):
        """get_file_previews returns empty list for a non-succeeded task."""
        task = await task_repo.create(
            installation_id="1",
            repository="o/r",
            base_branch="main",
            files=["a.md"],
            language="ko",
        )

        previews = await task_repo.get_file_previews(task.task_id)

        assert previews == []

    @pytest.mark.asyncio
    async def test_failed_task_stores_only_safe_error_info(
        self, task_repo: TranslationTaskRepository
    ):
        """Failed task persistence uses predefined error codes, not raw exceptions."""
        task = await task_repo.create(
            installation_id="1",
            repository="o/r",
            base_branch="main",
            files=["a.md"],
            language="es",
        )
        await task_repo.update_status(task.task_id, TaskStatus.RUNNING)

        result = await task_repo.update_status(
            task.task_id,
            TaskStatus.FAILED,
            error_code="file_read_error",
            error_message="Failed to read file from repository",
        )

        assert result is not None
        assert result.error_code == "file_read_error"
        # error_message must not contain stack traces or sensitive info
        assert "traceback" not in result.error_message.lower()
        assert "token" not in result.error_message.lower()
        assert "secret" not in result.error_message.lower()

    @pytest.mark.asyncio
    async def test_create_returns_domain_data(self, task_repo: TranslationTaskRepository):
        """Repository returns domain data, not ORM model."""
        result = await task_repo.create(
            installation_id="1",
            repository="o/r",
            base_branch="main",
            files=["a.md"],
            language="ja",
        )

        # Should have domain model attributes, not SQLAlchemy attributes
        assert hasattr(result, "task_id")
        assert hasattr(result, "status")
        assert not hasattr(result, "_sa_instance_state")


# --- InstallationAccountRepository ---


class TestInstallationAccountRepository:
    """Tests for InstallationAccountRepository upsert operations."""

    @pytest.mark.asyncio
    async def test_upsert_new_account(self, account_repo: InstallationAccountRepository):
        """Upsert creates a new record when installation_id does not exist."""
        result = await account_repo.upsert(
            installation_id=42,
            account_login="acme-corp",
            account_type="Organization",
            repository_selection="all",
        )

        assert result.installation_id == 42
        assert result.account_login == "acme-corp"
        assert result.account_type == "Organization"
        assert result.repository_selection == "all"

    @pytest.mark.asyncio
    async def test_upsert_existing_account_updates(self, account_repo: InstallationAccountRepository):
        """Upsert updates an existing record when installation_id already exists."""
        await account_repo.upsert(
            installation_id=42,
            account_login="old-login",
            account_type="User",
            repository_selection="selected",
        )

        result = await account_repo.upsert(
            installation_id=42,
            account_login="new-login",
            account_type="Organization",
            repository_selection="all",
        )

        assert result.installation_id == 42
        assert result.account_login == "new-login"
        assert result.account_type == "Organization"
        assert result.repository_selection == "all"

    @pytest.mark.asyncio
    async def test_upsert_returns_domain_data(self, account_repo: InstallationAccountRepository):
        """Repository returns domain data, not ORM model."""
        result = await account_repo.upsert(
            installation_id=1,
            account_login="test",
            account_type="User",
            repository_selection="all",
        )

        assert hasattr(result, "installation_id")
        assert hasattr(result, "account_login")
        assert not hasattr(result, "_sa_instance_state")
