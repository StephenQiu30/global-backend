"""Translation task API endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

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


class TranslationTaskRequest(BaseModel):
    """Request model for POST /api/translation-tasks."""

    installation_id: str = Field(..., min_length=1)
    repository: str = Field(..., min_length=1)
    base_branch: str = Field(..., min_length=1)
    files: List[str] = Field(..., min_length=1)
    language: str = Field(..., min_length=1)


def _get_task_runner() -> TaskRunner:
    """Dependency to get TaskRunner. Override in app factory."""
    raise NotImplementedError("TaskRunner not configured")


@router.post("/translation-tasks", response_model=TaskResult)
async def create_translation_task(
    request: TranslationTaskRequest,
    task_runner: TaskRunner = Depends(_get_task_runner),
) -> TaskResult:
    """Create and execute a translation task synchronously.

    Args:
        request: Translation task request
        task_runner: Task runner service

    Returns:
        TaskResult with status, PR info, or error details
    """
    from app.domain.task import Task

    task = Task(
        task_id="generated",
        installation_id=request.installation_id,
        repository=request.repository,
        base_branch=request.base_branch,
        files=request.files,
        language=request.language,
    )
    return await task_runner.run(task)
