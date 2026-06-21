"""Async session factory for FastAPI dependency injection."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.engine import get_engine

_session_factory: async_sessionmaker | None = None


def get_session_factory(database_url: str | None = None) -> async_sessionmaker:
    """Get or create the session factory singleton."""
    global _session_factory
    if _session_factory is None:
        engine = get_engine(database_url)
        _session_factory = async_sessionmaker(engine, expire_on_commit=False)
    return _session_factory


async def get_async_session(
    database_url: str | None = None,
) -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session."""
    factory = get_session_factory(database_url)
    async with factory() as session:
        yield session


def reset_session_factory():
    """Reset the session factory singleton (for testing)."""
    global _session_factory
    _session_factory = None
