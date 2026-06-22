## ADDED Requirements

### Requirement: Shared OpenAPI error response helper
`app/core/openapi.py` SHALL provide a `common_error_responses(*codes: ErrorCode) -> dict` function that returns an OpenAPI-compatible `responses` dict. Each entry SHALL use the global `ApiResponseVO[None]` schema as the response model.

#### Scenario: Helper returns error responses for given codes
- **WHEN** `common_error_responses(ErrorCode.VALIDATION_ERROR, ErrorCode.INTERNAL_ERROR)` is called
- **THEN** the result SHALL be a dict with keys `422` and `500`, each containing a `description` and `content` with the `ApiResponseVO` schema

#### Scenario: Helper with no codes returns empty dict
- **WHEN** `common_error_responses()` is called
- **THEN** the result SHALL be an empty dict

### Requirement: All endpoints document error responses
Every controller endpoint SHALL declare `responses` metadata for the error codes it can raise via `AppException` or centralized exception handlers.

#### Scenario: Endpoint with validation and not-found errors
- **WHEN** an endpoint can raise `VALIDATION_ERROR` (422) and `TASK_NOT_FOUND` (404)
- **THEN** its route decorator SHALL include `responses=common_error_responses(ErrorCode.VALIDATION_ERROR, ErrorCode.TASK_NOT_FOUND)`

### Requirement: No legacy error classes
`app/core/errors.py` SHALL NOT exist. The old `AppError` class SHALL be removed.

#### Scenario: Import check
- **WHEN** `from app.core.errors import AppError` is attempted
- **THEN** it SHALL raise `ModuleNotFoundError`

### Requirement: Architecture docs reflect global response contract
`docs/design/backend-engineering-architecture-review.md` SHALL document:
- The global `ApiResponseVO[T]` envelope
- The centralized exception handler pattern
- The `app/core/openapi.py` helper for OpenAPI error response metadata

#### Scenario: Doc reads
- **WHEN** the architecture doc is read
- **THEN** it SHALL reference `ApiResponseVO`, `ErrorCode`, `AppException`, and `common_error_responses`

### Requirement: OpenAPI tests verify error response coverage
`tests/controller/test_openapi_docs.py` SHALL verify that ALL endpoints have at least one non-2xx error response documented in the OpenAPI schema.

#### Scenario: All endpoints have error responses
- **WHEN** the OpenAPI schema is generated
- **THEN** every endpoint SHALL have at least one non-2xx response code documented
