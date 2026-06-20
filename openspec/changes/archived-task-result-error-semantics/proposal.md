# Proposal: Task Result & Error Semantics

## Summary

Standardize the task result structure and safe error mapping for translation tasks. The backend must return consistent, secure task results that support frontend display of success (PR link + file mappings) or failure (error code + message + retryability).

## Motivation

PRD 08 requires users to see processing, success, or failure after submitting a translation task. The domain models (`TaskStatus`, `FileMapping`, `TaskResult`) already exist from STE-325. This change adds the error handling layer: `AppError` exception type and safe API error mapping.

## Scope

### In Scope
- `AppError` exception with `code`, `message`, `retryable` fields
- Safe error mapping: internal errors -> sanitized API responses
- Error code registry with HTTP status mapping
- API response serialization that never leaks secrets, tokens, or stack traces

### Out of Scope
- Async queue processing, WebSocket, real-time progress
- Task persistence (database)
- Task creation/execution endpoints (covered by STE-325)
- GitHub API integration (covered by STE-327)

## Non-Goals

- Return raw stack traces or provider original responses to the client
- Implement full task lifecycle management
- Support task cancellation or retry workflows

## Impact

- New core module: `app/core/errors.py`
- Updated API module: `app/api/tasks.py` (add `map_error_to_response`)
- New test files: `tests/domain/test_task_result.py`, `tests/api/test_task_errors.py`

## Success Criteria

1. `AppError` carries code, message, and retryable flag
2. API error mapping converts `AppError` to safe HTTP responses
3. No raw exceptions, tokens, or stack traces in API responses
4. All tests pass: `pytest tests/domain/test_task_result.py tests/api/test_task_errors.py -v`
