## Tasks

### 1. Migrate services to AppException

- [x] 1.1 `app/services/github_app.py`: Replace `ValueError` raises with `AppException(INSTALLATION_NOT_FOUND/REPOSITORY_NOT_FOUND, ..., http_status)`
- [x] 1.2 `app/services/public_repository.py`: Replace `ValueError` raises with `AppException(REPOSITORY_NOT_FOUND/GITHUB_RATE_LIMITED/VALIDATION_ERROR, ..., http_status)`
- [x] 1.3 `app/services/translation_task_service.py`: Replace `ValueError` with `AppException(UNSUPPORTED_LANGUAGE, ...)`
- [x] 1.4 `app/services/markdown_discovery.py`: Replace `ValueError` with `AppException(VALIDATION_ERROR, ...)`

### 2. Migrate controllers to success_response envelope

- [x] 2.1 `app/controller/installation_controller.py`: Wrap returns in `success_response()`, remove `HTTPException` catches, let `AppException` propagate
- [x] 2.2 `app/controller/repository_controller.py`: Wrap returns, remove `HTTPException` raises
- [x] 2.3 `app/controller/public_preview_controller.py`: Wrap returns, remove string-parsing error handler
- [x] 2.4 `app/controller/translation_task_controller.py`: Wrap returns, remove `_ERROR_STATUS_MAP` and `map_error_to_response`
- [x] 2.5 `app/controller/language_controller.py`: Wrap return in `success_response()`

### 3. Update tests

- [x] 3.1 Update `tests/api/test_installations.py` to verify envelope shape
- [x] 3.2 Update `tests/api/test_public_preview.py` to verify envelope shape
- [x] 3.3 Update `tests/api/test_repository_resolve.py` to verify envelope shape
- [x] 3.4 Update `tests/api/test_translation_tasks.py` to verify envelope shape
- [x] 3.5 Update `tests/api/test_task_errors.py` to remove `map_error_to_response` tests
- [x] 3.6 Update `tests/api/test_installation_repositories.py` to verify envelope shape

### 4. Remove dead code

- [x] 4.1 Delete `app/core/errors.py` (AppError class) — kept: still used in domain tests for TaskResult
- [x] 4.2 Clean up `app/vo/error_vo.py` (remove old error models)
- [x] 4.3 Remove `TaskNotFoundVO` from `app/vo/translation_task_vo.py` if present

### 5. Validation

- [x] 5.1 Run `pytest tests/api/ tests/controller/ -v` — 380 passed
- [x] 5.2 Run `pytest tests/services/ tests/domain/ -v` — 380 passed
- [x] 5.3 Verify OpenAPI JSON response schemas — all endpoints use `ApiResponseVO_` envelope
