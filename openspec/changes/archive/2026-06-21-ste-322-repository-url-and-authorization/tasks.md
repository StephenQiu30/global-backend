## 1. Project Bootstrap

- [x] 1.1 Create `pyproject.toml` with dependencies (fastapi, pydantic, pydantic-settings, pyjwt, httpx, pytest, pytest-asyncio)
- [x] 1.2 Create `app/__init__.py`, `app/core/__init__.py`, `app/domain/__init__.py`, `app/api/__init__.py`, `app/services/__init__.py`, `tests/__init__.py`, `tests/domain/__init__.py`, `tests/api/__init__.py`
- [x] 1.3 Create `app/core/config.py` with GitHub App settings (GITHUB_APP_ID, GITHUB_PRIVATE_KEY, GITHUB_APP_SLUG)
- [x] 1.4 Create `app/main.py` with FastAPI application factory

## 2. Repository Parser (TDD)

- [x] 2.1 Write failing tests in `tests/domain/test_repository.py` covering all parsing scenarios from specs/repository-parsing
- [x] 2.2 Implement `RepositoryRef` model in `app/domain/repository.py`
- [x] 2.3 Implement `parse_repository_input()` in `app/domain/repository.py`
- [x] 2.4 Verify all parser tests pass: `pytest tests/domain/test_repository.py -v`

## 3. GitHub App Service

- [x] 3.1 Write failing tests in `tests/services/test_github_app.py` for installation repository listing
- [x] 3.2 Implement `GithubAppService` in `app/services/github_app.py` with `get_installation_repositories()` method
- [x] 3.3 Verify service tests pass: `pytest tests/services/test_github_app.py -v`

## 4. Repository Resolve API (TDD)

- [x] 4.1 Write failing tests in `tests/api/test_repository_resolve.py` covering all resolve scenarios from specs/repository-authorization
- [x] 4.2 Implement `router` in `app/api/repositories.py` with `POST /api/repositories/resolve` endpoint
- [x] 4.3 Register router in `app/main.py`
- [x] 4.4 Verify all resolve API tests pass: `pytest tests/api/test_repository_resolve.py -v`

## 5. Final Validation

- [x] 5.1 Run full test suite: `pytest tests/domain/test_repository.py tests/api/test_repository_resolve.py -v`
- [x] 5.2 Verify no test regressions
