"""AppException and global FastAPI exception handlers."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

from app.core.response import ErrorCode, error_response, get_http_status, get_trace_id


class AppException(Exception):
    """Structured application exception with ErrorCode, safe message, and HTTP status."""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        http_status: int,
        *,
        retryable: bool = False,
    ):
        self.code = code
        self.message = message
        self.http_status = http_status
        self.retryable = retryable
        super().__init__(message)


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        envelope = error_response(code=exc.code, message=exc.message)
        return JSONResponse(
            status_code=exc.http_status,
            content=envelope.model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        envelope = error_response(
            code=ErrorCode.VALIDATION_ERROR,
            message=str(exc.errors()),
        )
        return JSONResponse(status_code=422, content=envelope.model_dump())

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        # Use INTERNAL_ERROR for 5xx, generic code for others
        code = ErrorCode.INTERNAL_ERROR if exc.status_code >= 500 else ErrorCode.VALIDATION_ERROR
        envelope = error_response(code=code, message=message)
        return JSONResponse(status_code=exc.status_code, content=envelope.model_dump())

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        envelope = error_response(
            code=ErrorCode.INTERNAL_ERROR,
            message="An unexpected error occurred",
        )
        return JSONResponse(status_code=500, content=envelope.model_dump())
