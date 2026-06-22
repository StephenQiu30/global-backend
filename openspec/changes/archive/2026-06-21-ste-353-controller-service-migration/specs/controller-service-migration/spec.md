## Spec: Controller and Service Migration to Global Response Contract

### Requirements

1. **Service Layer Error Contract**
   - Services SHALL raise `AppException(ErrorCode, message, http_status)` for business errors that cross layer boundaries
   - Services SHALL NOT use `ValueError` strings as business error contracts
   - `AppException.http_status` SHALL match the semantic HTTP status code for the error

2. **Controller Success Response**
   - Controllers SHALL return `ApiResponseVO[T]` via `success_response(data)` for successful operations
   - The response envelope SHALL contain `code: "SUCCESS"`, `message: "OK"`, `data: <payload>`, `trace_id: <uuid>`

3. **Controller Error Handling**
   - Controllers SHALL NOT define `_ERROR_STATUS_MAP` dictionaries
   - Controllers SHALL NOT parse `ValueError` strings to determine HTTP status
   - Controllers SHALL NOT raise `HTTPException` directly for business errors
   - Controllers MAY let `AppException` propagate (handled by global exception handler)

4. **Error Response Format**
   - Error responses SHALL have `code` (uppercase `ErrorCode` enum), `message` (human-readable), `data: null`, `trace_id`
   - HTTP status codes SHALL remain semantically correct (400, 403, 404, 422, 429, 500, 502, 504)

5. **Dead Code Removal**
   - `AppError` class in `app/core/errors.py` — KEPT: still used in domain tests for TaskResult error semantics
   - Old error VO models in `app/vo/error_vo.py` SHALL be removed (`SimpleErrorVO`, `MessageErrorVO`, `RetryableErrorVO`, `CodeMessageErrorVO`)
   - `TaskNotFoundVO` in `app/vo/translation_task_vo.py` SHALL be removed if present

### Error Code Mapping

| ErrorCode | HTTP Status | Usage |
|-----------|-------------|-------|
| VALIDATION_ERROR | 422 | Request validation failures |
| INTERNAL_ERROR | 500 | Unexpected server errors |
| GITHUB_API_ERROR | 502 | GitHub API failures |
| TASK_NOT_FOUND | 404 | Translation task not found |
| INSTALLATION_NOT_FOUND | 404 | GitHub App installation not found |
| REPOSITORY_NOT_FOUND | 404 | Repository not found |
| REPOSITORY_NOT_INSTALLED | 400 | Repository not authorized |
| GITHUB_RATE_LIMITED | 429 | GitHub API rate limit |
| TRANSLATION_ERROR | 500 | Translation provider failures |
| UNSUPPORTED_LANGUAGE | 400 | Invalid language code |

### Validation

- `pytest tests/api/ tests/controller/ -v` — API integration tests pass
- `pytest tests/services/ tests/domain/ -v` — Service/domain unit tests pass
- OpenAPI JSON response schemas reference global envelope
