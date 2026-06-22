## Context

STE-353 migrated all controllers and services to the global response contract
(`ApiResponseVO[T]`, `AppException`, centralized exception handlers). However,
the OpenAPI schema still lacks error response documentation on individual
endpoints. The architecture doc (`docs/design/backend-engineering-architecture-review.md`)
still instructs "Endpoints must declare `responses` metadata for expected error
codes" but no controller does this. The legacy `AppError` class in
`app/core/errors.py` is unused and should be removed.

## Goal

- Provide a shared OpenAPI helper that generates `responses` metadata for
  common error codes using the global `ApiResponseVO[None]` schema.
- Add `responses` to each controller route decorator so the OpenAPI schema
  documents which error codes each endpoint can return.
- Remove the obsolete `AppError` class from `app/core/errors.py`.
- Update architecture docs to reflect the global response contract and the
  OpenAPI helper pattern.
- Ensure OpenAPI tests verify that all endpoints document error responses.

## Non-Goals

- No custom OpenAPI generator or schema post-processing.
- No frontend client regeneration.
- No cosmetic route reordering or unrelated Swagger tagging changes.

## OpenSpec Impact

Completes documentation and schema cleanup for the `add-global-api-response-contract`
change. The `task-result-errors` spec references the old `AppError` and
`map_error_to_response` pattern; this change supersedes those references.
