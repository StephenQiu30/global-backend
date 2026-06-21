"""Tests for SQLAlchemy ORM models."""

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.db.base import Base
from app.models.installation_account_model import InstallationAccountModel
from app.models.translation_task_model import TranslationTaskModel
from app.models.translation_file_model import TranslationFileModel


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


class TestInstallationAccountModel:
    """Tests for InstallationAccountModel ORM."""

    async def test_create_installation_account(self, session):
        """Creating an InstallationAccountModel persists with correct fields."""
        model = InstallationAccountModel(
            installation_id=12345,
            account_login="test-org",
            account_type="Organization",
        )
        session.add(model)
        await session.commit()
        await session.refresh(model)

        assert model.id is not None
        assert len(model.id) == 32  # uuid4().hex
        assert model.installation_id == 12345
        assert model.account_login == "test-org"
        assert model.account_type == "Organization"
        assert model.created_at is not None

    async def test_installation_id_unique(self, session):
        """Installation ID must be unique."""
        model1 = InstallationAccountModel(
            installation_id=12345,
            account_login="org-1",
            account_type="Organization",
        )
        session.add(model1)
        await session.commit()

        model2 = InstallationAccountModel(
            installation_id=12345,
            account_login="org-2",
            account_type="Organization",
        )
        session.add(model2)
        with pytest.raises(Exception):  # IntegrityError
            await session.commit()


class TestTranslationTaskModel:
    """Tests for TranslationTaskModel ORM."""

    async def test_create_translation_task(self, session):
        """Creating a TranslationTaskModel persists with correct fields."""
        model = TranslationTaskModel(
            task_id="abc123def456",
            installation_id="inst-123",
            repository="owner/repo",
            base_branch="main",
            source_files=["README.md", "docs/guide.md"],
            language="zh-CN",
            status="queued",
        )
        session.add(model)
        await session.commit()
        await session.refresh(model)

        assert model.id is not None
        assert len(model.id) == 32
        assert model.task_id == "abc123def456"
        assert model.installation_id == "inst-123"
        assert model.repository == "owner/repo"
        assert model.base_branch == "main"
        assert model.source_files == ["README.md", "docs/guide.md"]
        assert model.language == "zh-CN"
        assert model.status == "queued"
        assert model.pr_url is None
        assert model.pr_number is None
        assert model.file_mappings is None
        assert model.error_code is None
        assert model.error_message is None
        assert model.created_at is not None

    async def test_task_id_unique(self, session):
        """Task ID must be unique."""
        model1 = TranslationTaskModel(
            task_id="same-id",
            installation_id="inst-1",
            repository="owner/repo",
            base_branch="main",
            source_files=["README.md"],
            language="zh-CN",
        )
        session.add(model1)
        await session.commit()

        model2 = TranslationTaskModel(
            task_id="same-id",
            installation_id="inst-2",
            repository="owner/repo2",
            base_branch="main",
            source_files=["README.md"],
            language="ja",
        )
        session.add(model2)
        with pytest.raises(Exception):  # IntegrityError
            await session.commit()

    async def test_update_task_result(self, session):
        """Task result fields can be updated after creation."""
        model = TranslationTaskModel(
            task_id="update-test",
            installation_id="inst-123",
            repository="owner/repo",
            base_branch="main",
            source_files=["README.md"],
            language="zh-CN",
            status="queued",
        )
        session.add(model)
        await session.commit()

        model.status = "succeeded"
        model.pr_url = "https://github.com/owner/repo/pull/42"
        model.pr_number = 42
        model.file_mappings = [{"source_path": "README.md", "target_path": "README.zh-CN.md"}]
        await session.commit()
        await session.refresh(model)

        assert model.status == "succeeded"
        assert model.pr_url == "https://github.com/owner/repo/pull/42"
        assert model.pr_number == 42
        assert len(model.file_mappings) == 1

    async def test_task_json_columns(self, session):
        """JSON columns store and retrieve complex data."""
        files = [f"docs/file-{i}.md" for i in range(5)]
        mappings = [
            {"source_path": f"docs/file-{i}.md", "target_path": f"docs/file-{i}.zh-CN.md"}
            for i in range(5)
        ]
        model = TranslationTaskModel(
            task_id="json-test",
            installation_id="inst-123",
            repository="owner/repo",
            base_branch="main",
            source_files=files,
            language="zh-CN",
            status="succeeded",
            file_mappings=mappings,
        )
        session.add(model)
        await session.commit()
        await session.refresh(model)

        assert model.source_files == files
        assert model.file_mappings == mappings


class TestTranslationFileModel:
    """Tests for TranslationFileModel ORM."""

    async def test_create_translation_file(self, session):
        """Creating a TranslationFileModel persists with correct fields."""
        model = TranslationFileModel(
            task_id="task-123",
            source_path="README.md",
            target_path="README.zh-CN.md",
            status="translated",
        )
        session.add(model)
        await session.commit()
        await session.refresh(model)

        assert model.id is not None
        assert len(model.id) == 32
        assert model.task_id == "task-123"
        assert model.source_path == "README.md"
        assert model.target_path == "README.zh-CN.md"
        assert model.status == "translated"
        assert model.created_at is not None

    async def test_multiple_files_per_task(self, session):
        """Multiple file records can be associated with the same task."""
        for i in range(3):
            model = TranslationFileModel(
                task_id="task-multi",
                source_path=f"file-{i}.md",
                target_path=f"file-{i}.zh-CN.md",
                status="translated",
            )
            session.add(model)
        await session.commit()

        from sqlalchemy import select
        stmt = select(TranslationFileModel).where(
            TranslationFileModel.task_id == "task-multi"
        )
        result = await session.execute(stmt)
        files = list(result.scalars().all())
        assert len(files) == 3
