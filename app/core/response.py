"""Unified API response envelope, error codes, and trace ID support."""

from contextvars import ContextVar
from enum import Enum
from typing import Any, Generic, TypeVar
from uuid import uuid4

from fastapi import Request
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

T = TypeVar("T")

# --- Trace ID ---

_trace_id_ctx: ContextVar[str] = ContextVar("trace_id", default="")


def get_trace_id() -> str:
    """Return the current request trace ID, generating one if absent."""
    tid = _trace_id_ctx.get()
    if not tid:
        tid = str(uuid4())
        _trace_id_ctx.set(tid)
    return tid


class TraceIdMiddleware(BaseHTTPMiddleware):
    """Middleware that assigns a unique trace ID to every request."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        token = _trace_id_ctx.set(str(uuid4()))
        try:
            return await call_next(request)
        finally:
            _trace_id_ctx.reset(token)


# --- Error Code Enum ---


class ErrorCode(str, Enum):
    """Uppercase response codes for the unified API response envelope."""

    SUCCESS = "SUCCESS"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    GITHUB_API_ERROR = "GITHUB_API_ERROR"
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    INSTALLATION_NOT_FOUND = "INSTALLATION_NOT_FOUND"
    REPOSITORY_NOT_FOUND = "REPOSITORY_NOT_FOUND"
    REPOSITORY_NOT_INSTALLED = "REPOSITORY_NOT_INSTALLED"
    GITHUB_RATE_LIMITED = "GITHUB_RATE_LIMITED"
    TRANSLATION_ERROR = "TRANSLATION_ERROR"
    UNSUPPORTED_LANGUAGE = "UNSUPPORTED_LANGUAGE"


# --- Response Envelope ---


class ApiResponseVO(BaseModel, Generic[T]):
    """Unified API response envelope with code, message, data, and trace_id."""

    code: ErrorCode
    message: str
    data: T | None
    trace_id: str


# --- Response Helpers ---


def success_response(data: T, trace_id: str | None = None) -> ApiResponseVO[T]:
    """Build a success response envelope."""
    return ApiResponseVO(
        code=ErrorCode.SUCCESS,
        message="OK",
        data=data,
        trace_id=trace_id or get_trace_id(),
    )


def error_response(
    code: ErrorCode,
    message: str,
    trace_id: str | None = None,
) -> ApiResponseVO[None]:
    """Build an error response envelope."""
    return ApiResponseVO(
        code=code,
        message=message,
        data=None,
        trace_id=trace_id or get_trace_id(),
    )


# --- HTTP Status Mapping ---

ERROR_CODE_HTTP_STATUS: dict[ErrorCode, int] = {
    ErrorCode.VALIDATION_ERROR: 422,
    ErrorCode.INTERNAL_ERROR: 500,
    ErrorCode.GITHUB_API_ERROR: 502,
    ErrorCode.TASK_NOT_FOUND: 404,
    ErrorCode.INSTALLATION_NOT_FOUND: 404,
    ErrorCode.REPOSITORY_NOT_FOUND: 404,
    ErrorCode.REPOSITORY_NOT_INSTALLED: 400,
    ErrorCode.GITHUB_RATE_LIMITED: 429,
    ErrorCode.TRANSLATION_ERROR: 500,
    ErrorCode.UNSUPPORTED_LANGUAGE: 400,
}


def get_http_status(code: ErrorCode) -> int:
    """Return the HTTP status code for an ErrorCode, defaulting to 500."""
    return ERROR_CODE_HTTP_STATUS.get(code, 500)
