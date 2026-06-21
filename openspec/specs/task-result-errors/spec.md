# Specs: Task Result & Error Semantics

## TaskStatus Enum (existing from STE-325)

- `TaskStatus` is a `str, Enum` with values: `QUEUED`, `RUNNING`, `SUCCEEDED`, `FAILED`.
- Status values are lowercase strings: `"queued"`, `"running"`, `"succeeded"`, `"failed"`.

## TaskResult Model (existing from STE-325)

- `TaskResult` is a Pydantic `BaseModel`.
- `TaskResult.status` is of type `TaskStatus`.
- `TaskResult.pr_url` is `Optional[str]`, default `None`. Present only when status is `SUCCEEDED`.
- `TaskResult.pr_number` is `Optional[int]`, default `None`. Present only when status is `SUCCEEDED`.
- `TaskResult.mappings` is `Optional[List[FileMapping]]`, default `None`. Present only when status is `SUCCEEDED`.
- `TaskResult.error_code` is `Optional[str]`, default `None`. Present only when status is `FAILED`.
- `TaskResult.error_message` is `Optional[str]`, default `None`. Present only when status is `FAILED`.
- `TaskResult` serialization MUST NOT include fields with `None` values when `exclude_none=True`.

## AppError Exception (new)

- `AppError` SHALL extend `Exception`.
- `AppError` MUST have fields: `code: str`, `message: str`, `retryable: bool` (default `False`).
- `AppError.__init__` MUST accept `code`, `message`, and keyword-only `retryable`.
- `AppError` MUST be importable from `app.core.errors`.

## Safe Error Mapping (new)

- GIVEN an `AppError` with `code="github_permission_denied"` and `message="..."`, WHEN mapped to API response, THEN the response SHALL have `status_code=403` and `detail={"error": "github_permission_denied", "message": "...", "retryable": false}`.
- GIVEN an `AppError` with `code="model_timeout"` and `retryable=True`, WHEN mapped to API response, THEN the response SHALL have `status_code=504` and `detail` includes `"retryable": true`.
- GIVEN an unhandled `Exception`, WHEN caught by API error handler, THEN the response SHALL have `status_code=500` and `detail={"error": "internal_error", "message": "An unexpected error occurred", "retryable": false}`. The raw exception message MUST NOT be leaked.
- GIVEN any error response, WHEN serialized, THEN it MUST NOT contain `traceback`, `stack`, `token`, `secret`, `password`, or `authorization` fields.

## API Error Handler (new)

- `app.controller.translation_task_controller` SHALL provide a function `map_error_to_response(error: Exception) -> HTTPException` that converts `AppError` to `HTTPException` with safe detail dict.
- For unknown error codes, the handler SHALL default to `status_code=500` with `error="internal_error"`.
