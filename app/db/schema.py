"""Database schema initialization from ORM models."""

from sqlalchemy import create_engine

import app.models  # noqa: F401 — register models on Base.metadata
from app.core.config import Settings
from app.models.base import Base


def init_schema(database_url: str | None = None) -> None:
    """Create all tables defined in app.models."""
    url = database_url or Settings().database_url
    engine = create_engine(url)
    Base.metadata.create_all(engine)
