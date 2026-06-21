"""Tests for TranslationTaskRepository and InstallationAccountRepository."""

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.db.base import Base
from app.repositories.translation_task_repository import TranslationTaskRepository
from app.repositories.installation_account_repository import InstallationAccountRepository


@pytest.fixture
async def engine():
    """Create an in-memory SQLite async engine for testing."""
    eng = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest.fixture
async def session(engine):
    """Create an async session for testing."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as sess:
        yield sess


class TestTranslationTaskRepository:
    """Tests for TranslationTaskRepository."""

    async def test_create_task(self, session):
        """Creating a task returns a model with correct fields."""
        repo = TranslationTaskRepository(session)
        model = await repo.create_task(
            task_id="test-task-123",
            installation_id="inst-123",
            repository="owner/repo",
            base_branch="main",
            source_files=["README.md"],
            language="zh-CN",
        )
        assert model.task_id == "test-task-123"
        assert model.status == "queued"
        assert model.installation_id == "inst-123"

    async def test_get_by_task_id(self, session):
        """Getting a task by task_id returns the correct model."""
        repo = TranslationTaskRepository(session)
        await repo.create_task(
            task_id="find-me",
            installation_id="inst-123",
            repository="owner/repo",
            base_branch="main",
            source_files=["README.md"],
            language="zh-CN",
        )
        found = await repo.get_by_task_id("find-me")
        assert found is not None
        assert found.task_id == "find-me"

    async def test_get_by_task_id_not_found(self, session):
        """Getting a non-existent task returns None."""
        repo = TranslationTaskRepository(session)
        found = await repo.get_by_task_id("nonexistent")
        assert found is None

    async def test_update_status_to_succeeded(self, session):
        """Updating status to succeeded persists result fields."""
        repo = TranslationTaskRepository(session)
        await repo.create_task(
            task_id="update-test",
            installation_id="inst-123",
            repository="owner/repo",
            base_branch="main",
            source_files=["README.md"],
            language="zh-CN",
        )
        await repo.update_status(
            "update-test",
            "succeeded",
            pr_url="https://github.com/owner/repo/pull/1",
            pr_number=1,
            file_mappings=[{"source_path": "README.md", "target_path": "README.zh-CN.md"}],
        )
        updated = await repo.get_by_task_id("update-test")
        assert updated.status == "succeeded"
        assert updated.pr_url == "https://github.com/owner/repo/pull/1"
        assert updated.pr_number == 1
        assert len(updated.file_mappings) == 1

    async def test_update_status_to_failed(self, session):
        """Updating status to failed persists error fields."""
        repo = TranslationTaskRepository(session)
        await repo.create_task(
            task_id="fail-test",
            installation_id="inst-123",
            repository="owner/repo",
            base_branch="main",
            source_files=["README.md"],
            language="zh-CN",
        )
        await repo.update_status(
            "fail-test",
            "failed",
            error_code="translation_error",
            error_message="Translation provider returned an error",
        )
        updated = await repo.get_by_task_id("fail-test")
        assert updated.status == "failed"
        assert updated.error_code == "translation_error"
        assert updated.error_message == "Translation provider returned an error"

    async def test_update_nonexistent_task(self, session):
        """Updating a non-existent task is a no-op."""
        repo = TranslationTaskRepository(session)
        await repo.update_status("nonexistent", "failed")  # Should not raise

    async def test_get_file_previews(self, session):
        """Getting file previews returns records for the task."""
        repo = TranslationTaskRepository(session)
        await repo.create_task(
            task_id="preview-test",
            installation_id="inst-123",
            repository="owner/repo",
            base_branch="main",
            source_files=["README.md", "docs/guide.md"],
            language="zh-CN",
        )
        await repo.create_file_previews(
            "preview-test",
            [
                {"source_path": "README.md", "target_path": "README.zh-CN.md"},
                {"source_path": "docs/guide.md", "target_path": "docs/guide.zh-CN.md"},
            ],
        )
        previews = await repo.get_file_previews("preview-test")
        assert len(previews) == 2
        assert previews[0].source_path == "README.md"
        assert previews[1].source_path == "docs/guide.md"

    async def test_get_file_previews_empty(self, session):
        """Getting file previews for a task with no files returns empty list."""
        repo = TranslationTaskRepository(session)
        await repo.create_task(
            task_id="empty-preview",
            installation_id="inst-123",
            repository="owner/repo",
            base_branch="main",
            source_files=["README.md"],
            language="zh-CN",
        )
        previews = await repo.get_file_previews("empty-preview")
        assert previews == []


class TestInstallationAccountRepository:
    """Tests for InstallationAccountRepository."""

    async def test_upsert_new(self, session):
        """Upserting a new installation creates a record."""
        repo = InstallationAccountRepository(session)
        model = await repo.upsert(12345, "test-org", "Organization")
        assert model.installation_id == 12345
        assert model.account_login == "test-org"
        assert model.account_type == "Organization"

    async def test_upsert_existing(self, session):
        """Upserting an existing installation updates the record."""
        repo = InstallationAccountRepository(session)
        await repo.upsert(12345, "old-login", "Organization")
        updated = await repo.upsert(12345, "new-login", "User")
        assert updated.installation_id == 12345
        assert updated.account_login == "new-login"
        assert updated.account_type == "User"
