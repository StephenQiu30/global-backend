# Tasks: Task Result & Error Semantics

## Task 1: Domain Tests (`tests/domain/test_task_result.py`)

**Files:** `tests/domain/test_task_result.py`

- [x] 1.1 Write failing tests for `TaskStatus` enum values and type
- [x] 1.2 Write failing tests for `FileMapping` model serialization
- [x] 1.3 Write failing tests for `TaskResult` succeeded serialization (with `exclude_none`)
- [x] 1.4 Write failing tests for `TaskResult` failed serialization (with `exclude_none`)
- [x] 1.5 Write failing tests for `AppError` fields (code, message, retryable)

**Verification:** `pytest tests/domain/test_task_result.py -v` — 21 tests pass

## Task 2: Error Types (`app/core/errors.py`)

**Files:** `app/core/errors.py`

- [x] 2.1 Implement `AppError` with `code`, `message`, `retryable` fields
- [x] 2.2 Default `retryable=False`
- [x] 2.3 Extend `Exception`, `str(err)` returns message

**Verification:** `pytest tests/domain/test_task_result.py -v` — all pass

## Task 3: API Error Mapping (`app/api/tasks.py`)

**Files:** `app/api/tasks.py`, `tests/api/test_task_errors.py`

- [x] 3.1 Write failing tests for `map_error_to_response` with known `AppError` codes
- [x] 3.2 Write failing tests for `map_error_to_response` with unknown `AppError` code
- [x] 3.3 Write failing tests for `map_error_to_response` with unhandled `Exception`
- [x] 3.4 Write failing tests verifying no secret/token/stack leak in responses
- [x] 3.5 Implement `map_error_to_response` and error code registry

**Verification:** `pytest tests/api/test_task_errors.py -v` — 12 tests pass

## Task 4: Integration Verification

**Files:** None (validation only)

- [x] 4.1 Run full test suite: `pytest tests/domain/test_task_result.py tests/api/test_task_errors.py -v` — 33 passed
- [x] 4.2 Verify no raw exception messages leak in API responses
- [x] 4.3 Verify error codes match design registry

**Verification:** `pytest tests/domain/test_task_result.py tests/api/test_task_errors.py -v` — 33 passed
