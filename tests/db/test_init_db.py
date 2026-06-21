"""Tests for database schema initialization."""

from sqlalchemy import create_engine, inspect

from app.db.schema import init_schema


def test_init_schema_creates_orm_tables(tmp_path):
    """init_schema must create all tables defined in app.models."""
    url = f"sqlite:///{tmp_path / 'test.db'}"
    init_schema(url)

    engine = create_engine(url)
    inspector = inspect(engine)
    assert inspector.has_table("installation_accounts")
    assert inspector.has_table("translation_tasks")
    assert inspector.has_table("translation_files")
