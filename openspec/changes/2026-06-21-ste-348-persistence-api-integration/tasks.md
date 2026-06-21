## 1. Database Infrastructure

- [ ] 1.1 Add `sqlalchemy[asyncio]`, `aiosqlite` to `pyproject.toml` dependencies
- [ ] 1.2 Add `database_url` to `app/core/config.py` Settings
- [ ] 1.3 Create `app/db/__init__.py`, `app/db/base.py` (DeclarativeBase), `app/db/session.py` (get_async_session)

## 2. ORM Models with TDD

- [ ] 2.1 Create `tests/db/__init__.py` and `tests/db/test_models.py` with red tests
- [ ] 2.2 Create `app/models/__init__.py`, `app/models/installation_account_model.py`
- [ ] 2.3 Create `app/models/translation_task_model.py`
- [ ] 2.4 Create `app/models/translation_file_model.py`
- [ ] 2.5 Verify green: `pytest tests/db/test_models.py -v`

## 3. Repositories with TDD

- [ ] 3.1 Create `tests/repositories/__init__.py` and `tests/repositories/test_translation_task_repository.py` with red tests
- [ ] 3.2 Create `app/repositories/__init__.py`, `app/repositories/translation_task_repository.py`
- [ ] 3.3 Create `app/repositories/installation_account_repository.py`
- [ ] 3.4 Verify green: `pytest tests/repositories/test_translation_task_repository.py -v`

## 4. DTO / VO Schemas

- [ ] 4.1 Create `app/dto/__init__.py`, `app/dto/translation_task_dto.py`
- [ ] 4.2 Create `app/vo/__init__.py`, `app/vo/translation_task_vo.py`

## 5. Application Services

- [ ] 5.1 Create `app/services/translation_task_service.py`
- [ ] 5.2 Create `app/services/installation_service.py`

## 6. Queue Adapter

- [ ] 6.1 Create `app/queues/__init__.py`, `app/queues/translation_task_queue.py` (stub)

## 7. Controller Integration

- [ ] 7.1 Update `app/api/tasks.py`: add GET endpoints, modify POST to return task_id
- [ ] 7.2 Update `app/api/installations.py`: wire installation persistence
- [ ] 7.3 Update `app/main.py`: wire DB session, services, repositories

## 8. Persistence API Tests

- [ ] 8.1 Create `tests/api/test_persistence_api.py` with red tests
- [ ] 8.2 Implement controller wiring to make tests green
- [ ] 8.3 Verify green: `pytest tests/api/test_persistence_api.py -v`

## 9. Regression Check

- [ ] 9.1 Update `tests/api/test_translation_tasks.py` for new POST response format
- [ ] 9.2 Run full test suite: `pytest tests/ -v`
