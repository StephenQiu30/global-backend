"""SQLAlchemy async engine factory."""

from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import Settings

_engine = None


def get_engine(database_url: str | None = None):
    """Get or create the async engine singleton."""
    global _engine
    if _engine is None:
        url = database_url or Settings().database_url
        _engine = create_async_engine(url, echo=False)
    return _engine


def reset_engine():
    """Reset the engine singleton (for testing)."""
    global _engine
    _engine = None
