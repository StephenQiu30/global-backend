"""Controller for translation task endpoints."""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException

from app.core.errors import AppError
from app.dto.translation_task import (
    CreateTranslationTaskRequest,
    GetTranslationTaskFilePreviewsRequest,
    GetTranslationTaskStatusRequest,
)
from app.services.translation_task_service import TranslationTaskService
from app.vo.error_vo import MessageErrorVO, RetryableErrorVO
from app.vo.translation_task_vo import (
    FilePreviewVO,
    TaskNotFoundVO,
    TranslationTaskCreateVO,
    TranslationTaskStatusVO,
)

router = APIRouter(tags=["translation-tasks"])

_ERROR_STATUS_MAP: dict[str, int] = {
    "github_permission_denied": 403,
    "github_rate_limited": 429,
    "model_timeout": 504,
    "model_rate_limited": 429,
    "translation_failed": 500,
}


def map_error_to_response(error: Exception) -> HTTPException:
    """Convert an exception to a safe HTTPException."""
    if isinstance(error, AppError) and error.code in _ERROR_STATUS_MAP:
        return HTTPException(
            status_code=_ERROR_STATUS_MAP[error.code],
            detail={
                "error": error.code,
                "message": error.message,
                "retryable": error.retryable,
            },
        )

    return HTTPException(
        status_code=500,
        detail={
            "error": "internal_error",
            "message": "An unexpected error occurred",
            "retryable": False,
        },
    )


def _get_task_service() -> TranslationTaskService:
    """Dependency to get TranslationTaskService. Override in app factory."""
    raise NotImplementedError("TranslationTaskService not configured")


def _get_task_status_request(task_id: str) -> GetTranslationTaskStatusRequest:
    return GetTranslationTaskStatusRequest(task_id=task_id)


def _get_file_previews_request(
    task_id: str,
) -> GetTranslationTaskFilePreviewsRequest:
    return GetTranslationTaskFilePreviewsRequest(task_id=task_id)


@router.post(
    "/translation-tasks",
    response_model=TranslationTaskCreateVO,
    status_code=201,
    operation_id="create_translation_task",
    responses={
        400: {"model": MessageErrorVO, "description": "Invalid request"},
        422: {"model": RetryableErrorVO, "description": "Validation error"},
    },
)
async def create_translation_task(
    request: CreateTranslationTaskRequest,
    task_service: TranslationTaskService = Depends(_get_task_service),
) -> TranslationTaskCreateVO:
    """Create a translation task and enqueue for async execution."""
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
    request: Annotated[GetTranslationTaskStatusRequest, Depends(_get_task_status_request)],
    task_service: TranslationTaskService = Depends(_get_task_service),
) -> TranslationTaskStatusVO:
    """Retrieve persisted translation task status."""
    result = await task_service.get_task_status(request.task_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "task_not_found", "message": f"Task '{request.task_id}' not found"},
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
    request: Annotated[
        GetTranslationTaskFilePreviewsRequest,
        Depends(_get_file_previews_request),
    ],
    task_service: TranslationTaskService = Depends(_get_task_service),
) -> List[FilePreviewVO]:
    """Retrieve translated file preview metadata for a task."""
    result = await task_service.get_file_previews(request.task_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "task_not_found", "message": f"Task '{request.task_id}' not found"},
        )
    return result
