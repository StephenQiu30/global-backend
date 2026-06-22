## Context

All controllers use `response_model=ApiResponseVO[...]` for success responses
but none declare `responses={...}` for error codes. The OpenAPI schema therefore
lacks error response documentation. The centralized exception handlers in
`app/core/exceptions.py` handle all error-to-envelope conversion, but the
OpenAPI schema doesn't reflect this.

## Decisions

### 1. Shared OpenAPI helper in `app/core/openapi.py`

A small module providing:
- `error_response_dict(status_code, description)` → OpenAPI response dict
- `common_error_responses(*codes)` → merged `responses` dict for route decorators
- Pre-built tuples: `VALIDATION_ERRORS`, `NOT_FOUND_ERRORS`, `SERVER_ERRORS`

This avoids repeating `{422: {...}, 500: {...}}` on every route.

### 2. Controller routes use the helper

Each route decorator adds `responses=common_error_responses(...)` with the
specific `ErrorCode` values it can raise. This keeps the OpenAPI schema accurate
without per-endpoint VO classes.

### 3. Remove `app/core/errors.py`

The `AppError` class is unused after STE-353. Remove the file entirely.

### 4. Update architecture docs

Update `docs/design/backend-engineering-architecture-review.md`:
- Document the global response envelope contract
- Document the centralized exception handler pattern
- Update the Swagger/OpenAPI section to reference the shared helper
- Document `app/core/openapi.py` in the module layout

### 5. Update OpenAPI tests

Enhance `tests/controller/test_openapi_docs.py`:
- Verify ALL endpoints have at least one error response documented
- Verify error responses use the global `ApiResponseVO` schema shape
- Keep existing accessibility and path tests

## File Structure

```text
app/core/openapi.py                          # NEW: shared OpenAPI helper
app/core/errors.py                           # DELETE: unused AppError
app/controller/installation_controller.py    # ADD responses
app/controller/repository_controller.py      # ADD responses
app/controller/translation_task_controller.py # ADD responses
app/controller/language_controller.py        # ADD responses
app/controller/public_preview_controller.py  # ADD responses
docs/design/backend-engineering-architecture-review.md  # UPDATE
tests/controller/test_openapi_docs.py        # UPDATE
tests/core/test_openapi.py                   # NEW: tests for the helper
```
