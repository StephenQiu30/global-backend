## 1. Dependencies & Base Setup

- [ ] 1.1 Add sqlalchemy, alembic, asyncpg, aiosqlite to pyproject.toml
- [ ] 1.2 Create `app/db/__init__.py`, `app/db/base.py` with DeclarativeBase
- [ ] 1.3 Create `app/db/session.py` with async engine and session factory

## 2. ORM Models (TDD)

- [ ] 2.1 Write failing tests in `tests/db/test_models.py` covering InstallationAccountModel mapping and constraints
- [ ] 2.2 Implement `InstallationAccountModel` in `app/models/installation_account_model.py`
- [ ] 2.3 Write failing tests for TranslationTaskModel mapping, indexes, JSON columns
- [ ] 2.4 Implement `TranslationTaskModel` in `app/models/translation_task_model.py`
- [ ] 2.5 Write failing tests for TranslationFileModel mapping
- [ ] 2.6 Implement `TranslationFileModel` in `app/models/translation_file_model.py`
- [ ] 2.7 Verify all model tests pass: `pytest tests/db/test_models.py -v`

## 3. Alembic Setup

- [ ] 3.1 Create `alembic.ini` with async PG connection string
- [ ] 3.2 Create `alembic/env.py` with async support and model import
- [ ] 3.3 Generate initial migration `alembic/versions/*_add_translation_persistence.py`
- [ ] 3.4 Verify migration SQL contains correct tables, columns, indexes

## 4. Final Validation

- [ ] 4.1 Run full test suite: `pytest tests/db/test_models.py -v`
- [ ] 4.2 Verify no import of domain/DTO/controller modules in models
- [ ] 4.3 Review migration file for nullable constraints and index correctness
