"""Tests for InstallationAccountRepository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.repositories.installation_account_repository import InstallationAccountRepository


@pytest_asyncio.fixture
async def engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine):
    """Create a test session."""
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def repo(session):
    """Create an InstallationAccountRepository instance."""
    return InstallationAccountRepository(session)


@pytest.mark.asyncio
async def test_upsert_new_installation(repo):
    """Test upserting a new installation account."""
    result = await repo.upsert(
        installation_id=12345,
        account_login="testuser",
        account_type="User",
        repository_selection="all",
    )

    assert result.installation_id == 12345
    assert result.account_login == "testuser"
    assert result.account_type == "User"
    assert result.repository_selection == "all"


@pytest.mark.asyncio
async def test_upsert_existing_installation(repo):
    """Test upserting an existing installation account updates it."""
    # Create initial
    await repo.upsert(
        installation_id=12345,
        account_login="testuser",
        account_type="User",
        repository_selection="all",
    )

    # Update
    result = await repo.upsert(
        installation_id=12345,
        account_login="newlogin",
        account_type="Organization",
        repository_selection="selected",
    )

    assert result.installation_id == 12345
    assert result.account_login == "newlogin"
    assert result.account_type == "Organization"
    assert result.repository_selection == "selected"


@pytest.mark.asyncio
async def test_get_by_installation_id_existing(repo):
    """Test getting an existing installation account."""
    await repo.upsert(
        installation_id=12345,
        account_login="testuser",
        account_type="User",
        repository_selection="all",
    )

    result = await repo.get_by_installation_id(12345)

    assert result is not None
    assert result.installation_id == 12345
    assert result.account_login == "testuser"


@pytest.mark.asyncio
async def test_get_by_installation_id_nonexistent(repo):
    """Test getting a non-existent installation account returns None."""
    result = await repo.get_by_installation_id(99999)
    assert result is None
