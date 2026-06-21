# Global Response And Exception Linear Task Breakdown

> This document decomposes the global API response and global exception
> handling work into execution-ready Linear issue bodies. The target behavior is
> a single enterprise-style response envelope for both success and error
> responses, with uppercase enum response codes and centralized exception
> handling.

## Task 1: Define OpenSpec Contract For Global API Response And Exceptions

## Goal
- Establish the approved SDD contract for one global API response envelope,
  uppercase enum response codes, and centralized exception handling.

## Task Description
- Background: Controllers currently define `responses={...}` and error bodies
  endpoint by endpoint. Error payload shapes are inconsistent (`error`,
  `error_code`, optional `retryable`), and some controllers map exceptions by
  parsing strings or maintaining local maps.
- Expected change: Create or update an OpenSpec change that defines the global
  response envelope for success and failure:
  `{ "code": "SUCCESS", "message": "OK", "data": ..., "trace_id": "..." }`.
  Error responses use uppercase enum codes such as `GITHUB_API_ERROR`,
  `TASK_NOT_FOUND`, and `VALIDATION_ERROR`.
- OpenSpec impact: New change under
  `openspec/changes/add-global-api-response-contract/`.

## Scope Boundaries
- In scope: OpenSpec proposal, spec deltas, design notes, and task checklist for
  global response and exception behavior.
- Out of scope: Production code, controller migration, frontend migration, and
  compatibility layers not explicitly approved by the spec.
- Explicit non-goals: No all-HTTP-200 response policy, no middleware-only
  response wrapping that breaks FastAPI OpenAPI accuracy, no broad refactor of
  unrelated business logic.

## Acceptance Criteria
- OpenSpec requires all API success responses to use the same outer response
  envelope with `code`, `message`, `data`, and `trace_id`.
- OpenSpec requires all API error responses to use the same outer response
  envelope with `data: null`.
- OpenSpec defines uppercase enum response codes and includes `SUCCESS`,
  `VALIDATION_ERROR`, `INTERNAL_ERROR`, `GITHUB_API_ERROR`, `TASK_NOT_FOUND`,
  `INSTALLATION_NOT_FOUND`, `REPOSITORY_NOT_FOUND`, `REPOSITORY_NOT_INSTALLED`,
  `GITHUB_RATE_LIMITED`, `TRANSLATION_ERROR`, and `UNSUPPORTED_LANGUAGE`.
- OpenSpec states that HTTP status codes keep their semantics; errors are not
  forced into HTTP 200.
- OpenSpec states that controllers should not maintain local error maps or parse
  exception strings as the cross-layer error contract.

## Validation
- Automated: Run the repository OpenSpec validation command if available, plus
  `bash scripts/validate-repository.sh`.
- Manual: Review the spec against current controllers that define
  `responses={...}` and current error VOs in `app/vo/error_vo.py`.
- Agent Review focus: Confirm the contract is global but not overdesigned, and
  confirm it does not require frontend changes inside this backend task.

## Deliverables
- `openspec/changes/add-global-api-response-contract/proposal.md`
- `openspec/changes/add-global-api-response-contract/specs.md`
- `openspec/changes/add-global-api-response-contract/design.md`
- `openspec/changes/add-global-api-response-contract/tasks.md`

---

## Task 2: Add Global Response VO, ErrorCode Enum, And Exception Handlers

## Goal
- Provide the backend primitives that every controller can use for consistent
  success and error response bodies.

## Task Description
- Background: The backend has `AppError` with string codes, several error VO
  shapes, and controller-local error mapping logic.
- Expected change: Add a generic response VO, an uppercase `ErrorCode` enum, an
  `AppException`, request trace ID support, and FastAPI exception handlers for
  `AppException`, request validation errors, `HTTPException`, and unexpected
  exceptions.
- OpenSpec impact: Implements the core runtime portion of
  `add-global-api-response-contract`.

## Scope Boundaries
- In scope: `app/core/response.py`, `app/core/exceptions.py` or equivalent,
  global exception handler registration in the app factory, unit tests for
  response building and exception handling.
- Out of scope: Migrating every controller endpoint in this task, changing
  database schemas, changing queue behavior, or changing task runner error
  persistence.
- Explicit non-goals: No custom dependency injection framework, no response
  envelope middleware that hides OpenAPI response models, no stack trace leakage
  in API responses.

## Acceptance Criteria
- `ErrorCode` is a string enum with uppercase values and includes the codes
  approved by OpenSpec.
- `ApiResponseVO[T]` or equivalent exposes exactly `code`, `message`, `data`,
  and `trace_id`.
- Successful response helper returns `code=SUCCESS`, `message=OK`, caller data,
  and the request trace ID.
- Error response helper returns enum code, safe message, `data=None`, and the
  request trace ID.
- `AppException` carries `ErrorCode`, safe message, HTTP status code, and
  optional retryability metadata for future internal use.
- Global handlers return the unified envelope for `AppException`,
  `RequestValidationError`, `HTTPException`, and unexpected `Exception`.
- Unexpected exceptions map to `INTERNAL_ERROR` with a safe generic message.

## Validation
- Automated:
  `pytest tests/core/test_response.py tests/core/test_exception_handlers.py -v`
- Automated: `pytest tests/controller/test_openapi_docs.py -v`
- Manual: Trigger a validation error through `TestClient` and verify the
  response body includes uppercase `VALIDATION_ERROR` and a `trace_id`.
- Agent Review focus: Confirm no endpoint-specific behavior is migrated before
  the global primitives are tested, and confirm no secrets or stack traces are
  included in error messages.

## Deliverables
- `app/core/response.py`
- `app/core/exceptions.py`
- Updated `app/main.py`
- `tests/core/test_response.py`
- `tests/core/test_exception_handlers.py`

---

## Task 3: Migrate Controllers And Services To Global Response Contract

## Goal
- Make existing API endpoints return the unified response envelope and raise
  `AppException` instead of hand-written `HTTPException` or string-parsed
  `ValueError` mappings.

## Task Description
- Background: Installation, repository, public preview, and translation task
  controllers currently define local error responses and raise `HTTPException`
  directly. Some services use `ValueError` strings as business error contracts.
- Expected change: Update controllers to return `ApiResponseVO[...]` success
  envelopes and migrate business errors to `AppException(ErrorCode, ...)`.
  Services should raise typed application exceptions where the error crosses a
  layer boundary.
- OpenSpec impact: Implements controller and service migration for
  `add-global-api-response-contract`.

## Scope Boundaries
- In scope: Existing backend endpoints under `app/controller/`, service-layer
  business errors that are currently mapped by controllers, and API tests for
  existing endpoints.
- Out of scope: Frontend changes, new endpoints, new business capabilities,
  database migrations, and queue topology changes.
- Explicit non-goals: No compatibility response shape with both `error` and
  `error_code`; no new pagination or metadata envelope; no all-at-once rewrite
  of unrelated domain validation rules.

## Acceptance Criteria
- Every existing API success response body has outer fields `code`, `message`,
  `data`, and `trace_id`.
- Every existing API error response body has outer fields `code`, `message`,
  `data`, and `trace_id`, with `data` set to `null`.
- Error `code` values are uppercase enum values, not string literals scattered
  in controllers.
- Controllers do not define endpoint-local `_ERROR_STATUS_MAP` dictionaries.
- Controllers do not parse `ValueError` strings to decide HTTP status for
  cross-layer business errors.
- Existing HTTP status semantics remain unchanged for validation, not found,
  forbidden, rate-limit, upstream GitHub, and translation errors.

## Validation
- Automated: `pytest tests/api/ tests/controller/ -v`
- Automated: `pytest tests/services/ tests/domain/ -v`
- Manual: Inspect OpenAPI JSON and verify response schemas reference the global
  response envelope for migrated endpoints.
- Agent Review focus: Confirm endpoint behavior is preserved except for the
  documented response envelope, and confirm controller/service boundaries do not
  drift into unrelated refactoring.

## Deliverables
- Updated files under `app/controller/`
- Updated service errors under `app/services/` where needed
- Updated `app/vo/error_vo.py` or replacement global response VO module
- Updated API/controller tests

---

## Task 4: Consolidate Swagger Error Responses And Documentation

## Goal
- Make Swagger/OpenAPI and project docs describe the global response contract
  once instead of repeating bespoke error response definitions per endpoint.

## Task Description
- Background: Current route decorators repeat `responses={...}` with endpoint
  specific VO classes. This creates drift and makes global response behavior
  hard to review.
- Expected change: Add a small shared helper for common OpenAPI error response
  metadata, remove obsolete error VO classes, update docs, and ensure OpenAPI
  tests enforce the global response contract.
- OpenSpec impact: Completes documentation and schema cleanup for
  `add-global-api-response-contract`.

## Scope Boundaries
- In scope: OpenAPI helper, route decorator cleanup, response documentation,
  architecture docs, and tests that guard the global response envelope.
- Out of scope: Frontend OpenAPI client generation, versioned API compatibility
  layer, and unrelated Swagger tagging changes.
- Explicit non-goals: No large custom OpenAPI generator, no duplicated per-code
  VO classes, no cosmetic-only route reordering.

## Acceptance Criteria
- Route decorators no longer hand-write repetitive `responses={404: ..., 502:
  ...}` blocks when a shared helper can express the same global response
  contract.
- Obsolete error VO classes are removed or retained only when still referenced
  by tests proving a migration boundary.
- `docs/design/backend-engineering-architecture-review.md` documents the global
  response and exception boundary.
- OpenAPI tests verify global response schemas and stable Swagger availability
  at `/docs` and `/openapi.json`.
- Full repository validation passes.

## Validation
- Automated: `pytest tests/controller/test_openapi_docs.py -v`
- Automated: `pytest tests/api/ -v`
- Automated: `pytest tests/ -v`
- Automated: `bash scripts/validate-repository.sh`
- Manual: Open `/docs` locally and verify common response shape is visible on
  representative installation, repository, translation task, and public preview
  endpoints.
- Agent Review focus: Confirm OpenAPI cleanup stays small and does not hide
  endpoint-specific status codes or response data models.

## Deliverables
- Shared OpenAPI response helper module if needed
- Updated controller decorators
- Updated error/response VO modules
- Updated architecture docs
- Updated OpenAPI/API tests
