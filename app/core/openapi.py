"""Shared OpenAPI error response metadata for route decorators."""

from app.core.response import ApiResponseVO, ErrorCode, ERROR_CODE_HTTP_STATUS

# Pre-built error code tuples for common endpoint patterns.
VALIDATION_ERRORS: tuple[ErrorCode, ...] = (ErrorCode.VALIDATION_ERROR,)
NOT_FOUND_ERRORS: tuple[ErrorCode, ...] = (
    ErrorCode.TASK_NOT_FOUND,
    ErrorCode.REPOSITORY_NOT_FOUND,
    ErrorCode.INSTALLATION_NOT_FOUND,
)
SERVER_ERRORS: tuple[ErrorCode, ...] = (ErrorCode.INTERNAL_ERROR,)


def _error_schema() -> dict:
    """Return the OpenAPI schema reference for ApiResponseVO error responses."""
    return {"$ref": "#/components/schemas/ApiResponseVO_None_"}


def common_error_responses(*codes: ErrorCode) -> dict[int, dict]:
    """Build an OpenAPI ``responses`` dict for the given ErrorCode values.

    Each ErrorCode maps to its HTTP status via ``ERROR_CODE_HTTP_STATUS``.
    When multiple codes share the same HTTP status, the descriptions are merged.

    Returns:
        A dict mapping HTTP status codes to OpenAPI response metadata.
    """
    if not codes:
        return {}

    by_status: dict[int, list[str]] = {}
    for code in codes:
        status = ERROR_CODE_HTTP_STATUS.get(code, 500)
        description = code.value.replace("_", " ").title()
        by_status.setdefault(status, []).append(description)

    responses: dict[int, dict] = {}
    for status, descriptions in by_status.items():
        label = " · ".join(descriptions)
        responses[status] = {
            "description": label,
            "content": {"application/json": {"schema": _error_schema()}},
        }

    return responses
