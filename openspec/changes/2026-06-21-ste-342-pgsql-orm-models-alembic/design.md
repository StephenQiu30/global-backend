## Architecture

```
app/
  db/
    __init__.py
    base.py          # DeclarativeBase, Base class
    session.py       # async engine, session factory
  models/
    __init__.py
    installation_account_model.py
    translation_task_model.py
    translation_file_model.py
alembic/
  env.py
  versions/
    20260621_add_translation_persistence.py
alembic.ini
tests/
  db/
    __init__.py
    conftest.py      # SQLite in-memory async fixtures
    test_models.py
```

## Key Decisions

1. **Async engine**: Use `create_async_engine` with `asyncpg` driver for production, `aiosqlite` for tests.
2. **JSON columns**: `source_files` and `file_mappings` use `JSON` type (not JSONB) for portability; tests use SQLite which doesn't support JSONB.
3. **UUID PKs**: Database-generated via `gen_random_uuid()` in PG, `hex(uuid4())` as Python-side default for SQLite test compatibility.
4. **No FK constraints**: `installation_id` and `task_id` are logical references, not foreign keys, to avoid coupling tables at DB level.
5. **Timestamp defaults**: `func.now()` at DB level, `datetime.now(UTC)` as Python default for test compatibility.
6. **Test strategy**: SQLite in-memory with aiosqlite for fast model mapping/constraint tests; PG-specific tests deferred to integration environment.

## Migration Strategy

Single initial migration creates all three tables. Future schema changes get individual migration scripts.
