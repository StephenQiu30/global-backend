"""Controller for translation task endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.errors import AppError
from app.domain.languages import validate_language_code
from app.domain.task import Task, TaskResult
from app.services.task_runner import TaskRunner
from app.services.translation_task_service import TranslationTaskService
from app.vo.translation_task_vo import (
    TranslationTaskCreateVO,
    TranslationTaskStatusVO,
    FilePreviewVO,
    TaskNotFoundVO,
)

router = APIRouter(tags=["translation-tasks"])

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


class ErrorResponse(BaseModel):
    """Structured error response."""

    error: str
    message: str
    retryable: bool = False


def _get_task_runner() -> TaskRunner:
    """Dependency to get TaskRunner. Override in app factory."""
    raise NotImplementedError("TaskRunner not configured")


def _get_task_service() -> TranslationTaskService:
    """Dependency to get TranslationTaskService. Override in app factory."""
    raise NotImplementedError("TranslationTaskService not configured")


@router.post(
    "/translation-tasks",
    response_model=TranslationTaskCreateVO,
    status_code=201,
    operation_id="create_translation_task",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
async def create_translation_task(
    request: TranslationTaskRequest,
    task_service: TranslationTaskService = Depends(_get_task_service),
) -> TranslationTaskCreateVO:
    """Create a translation task and enqueue for async execution.

    Args:
        request: Translation task creation request.
        task_service: TranslationTaskService dependency.

    Returns:
        TranslationTaskCreateVO with task_id and queued status.

    Raises:
        HTTPException: 400 for unsupported language, 422 for validation errors.
    """
    try:
        return await task_service.create_task(
            installation_id=request.installation_id,
            repository=request.repository,
            base_branch=request.base_branch,
            files=request.files,
            language=request.language,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "unsupported_language",
                "message": str(exc),
            },
        )


@router.get(
    "/translation-tasks/{task_id}",
    response_model=TranslationTaskStatusVO,
    operation_id="get_task_status",
    responses={
        404: {"model": TaskNotFoundVO, "description": "Task not found"},
    },
)
async def get_task_status(
    task_id: str,
    task_service: TranslationTaskService = Depends(_get_task_service),
) -> TranslationTaskStatusVO:
    """Retrieve persisted translation task status.

    Args:
        task_id: The translation task identifier.
        task_service: TranslationTaskService dependency.

    Returns:
        TranslationTaskStatusVO with task status and result.

    Raises:
        HTTPException: 404 if task not found.
    """
    result = await task_service.get_task_status(task_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "task_not_found", "message": f"Task '{task_id}' not found"},
        )
    return result


@router.get(
    "/translation-tasks/{task_id}/file-previews",
    response_model=List[FilePreviewVO],
    operation_id="get_file_previews",
    responses={
        404: {"model": TaskNotFoundVO, "description": "Task not found"},
    },
)
async def get_file_previews(
    task_id: str,
    task_service: TranslationTaskService = Depends(_get_task_service),
) -> List[FilePreviewVO]:
    """Retrieve translated file preview metadata for a task.

    Args:
        task_id: The translation task identifier.
        task_service: TranslationTaskService dependency.

    Returns:
        List of FilePreviewVO with file preview metadata.

    Raises:
        HTTPException: 404 if task not found.
    """
    result = await task_service.get_file_previews(task_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "task_not_found", "message": f"Task '{task_id}' not found"},
        )
    return result
