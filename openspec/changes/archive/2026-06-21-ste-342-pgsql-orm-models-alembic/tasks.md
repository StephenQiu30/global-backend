## 1. Dependencies & Base Setup

- [x] 1.1 Add sqlalchemy, alembic, asyncpg, aiosqlite to pyproject.toml
- [x] 1.2 Create `app/db/__init__.py`, `app/db/base.py` with DeclarativeBase
- [x] 1.3 Create `app/db/session.py` with async engine and session factory

## 2. ORM Models (TDD)

- [x] 2.1 Write failing tests in `tests/db/test_models.py` covering InstallationAccountModel mapping and constraints
- [x] 2.2 Implement `InstallationAccountModel` in `app/models/installation_account_model.py`
- [x] 2.3 Write failing tests for TranslationTaskModel mapping, indexes, JSON columns
- [x] 2.4 Implement `TranslationTaskModel` in `app/models/translation_task_model.py`
- [x] 2.5 Write failing tests for TranslationFileModel mapping
- [x] 2.6 Implement `TranslationFileModel` in `app/models/translation_file_model.py`
- [x] 2.7 Verify all model tests pass: `pytest tests/db/test_models.py -v`

## 3. Alembic Setup

- [x] 3.1 Create `alembic.ini` with async PG connection string
- [x] 3.2 Create `alembic/env.py` with async support and model import
- [x] 3.3 Generate initial migration `alembic/versions/*_add_translation_persistence.py`
- [x] 3.4 Verify migration SQL contains correct tables, columns, indexes

## 4. Final Validation

- [x] 4.1 Run full test suite: `pytest tests/db/test_models.py -v`
- [x] 4.2 Verify no import of domain/DTO/controller modules in models
- [x] 4.3 Review migration file for nullable constraints and index correctness
