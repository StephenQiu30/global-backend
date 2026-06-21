"""Translation task API endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from app.application.translation_task_service import (
    TranslationTaskRequest,
    TranslationTaskService,
    UnsupportedLanguageError,
)
from app.core.errors import AppError
from app.domain.task import TaskResult
from app.services.task_runner import TaskRunner

router = APIRouter()

# Error code -> HTTP status mapping for known application errors.
_ERROR_STATUS_MAP: dict[str, int] = {
    "github_permission_denied": 403,
    "github_rate_limited": 429,
    "model_timeout": 504,
    "model_rate_limited": 429,
    "translation_failed": 500,
}


def map_error_to_response(error: Exception) -> HTTPException:
    """Convert an exception to a safe HTTPException.

    Maps known AppError codes to appropriate HTTP status codes.
    Unknown errors get a generic 500 response that never leaks
    internal details like stack traces, tokens, or secrets.

    Args:
        error: The exception to map.

    Returns:
        HTTPException with safe detail dict.
    """
    if isinstance(error, AppError) and error.code in _ERROR_STATUS_MAP:
        return HTTPException(
            status_code=_ERROR_STATUS_MAP[error.code],
            detail={
                "error": error.code,
                "message": error.message,
                "retryable": error.retryable,
            },
        )

    # Unknown AppError or unhandled exception: generic safe response.
    return HTTPException(
        status_code=500,
        detail={
            "error": "internal_error",
            "message": "An unexpected error occurred",
            "retryable": False,
        },
    )


def _get_task_runner() -> TaskRunner:
    """Dependency to get TaskRunner. Override in app factory."""
    raise NotImplementedError("TaskRunner not configured")


def _get_translation_task_service(
    task_runner: TaskRunner = Depends(_get_task_runner),
) -> TranslationTaskService:
    """Dependency to get TranslationTaskService."""
    return TranslationTaskService(task_runner=task_runner)


@router.post("/translation-tasks", response_model=TaskResult)
async def create_translation_task(
    request: TranslationTaskRequest,
    service: TranslationTaskService = Depends(_get_translation_task_service),
) -> TaskResult:
    """Create and execute a translation task synchronously.

    Args:
        request: Translation task request
        service: Translation task service

    Returns:
        TaskResult with status, PR info, or error details
    """
    try:
        return await service.create_task(request)
    except UnsupportedLanguageError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "unsupported_language",
                "message": f"Language '{e.language}' is not supported",
            },
        )
