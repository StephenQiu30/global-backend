"""Controller for translation task endpoints."""

from typing import Annotated, List

from fastapi import APIRouter, Depends

from app.core.exceptions import AppException
from app.core.openapi import common_error_responses
from app.core.response import ErrorCode, ApiResponseVO, success_response
from app.dto.translation_task import (
    CreateTranslationTaskRequest,
    GetTranslationTaskFilePreviewsRequest,
    GetTranslationTaskStatusRequest,
)
from app.services.translation_task_service import TranslationTaskService
from app.vo.translation_task_vo import (
    FilePreviewVO,
    TranslationTaskCreateVO,
    TranslationTaskStatusVO,
)

router = APIRouter(tags=["translation-tasks"])


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
    response_model=ApiResponseVO[TranslationTaskCreateVO],
    status_code=201,
    operation_id="create_translation_task",
    responses=common_error_responses(
        ErrorCode.VALIDATION_ERROR,
        ErrorCode.GITHUB_API_ERROR,
        ErrorCode.REPOSITORY_NOT_FOUND,
        ErrorCode.INTERNAL_ERROR,
    ),
)
async def create_translation_task(
    request: CreateTranslationTaskRequest,
    task_service: TranslationTaskService = Depends(_get_task_service),
) -> ApiResponseVO[TranslationTaskCreateVO]:
    """Create a translation task and enqueue for async execution."""
    result = await task_service.create_task(
        installation_id=request.installation_id,
        repository=request.repository,
        base_branch=request.base_branch,
        files=request.files,
        language=request.language,
    )
    return success_response(result)


@router.get(
    "/translation-tasks/{task_id}",
    response_model=ApiResponseVO[TranslationTaskStatusVO],
    operation_id="get_task_status",
    responses=common_error_responses(
        ErrorCode.TASK_NOT_FOUND,
        ErrorCode.INTERNAL_ERROR,
    ),
)
async def get_task_status(
    request: Annotated[GetTranslationTaskStatusRequest, Depends(_get_task_status_request)],
    task_service: TranslationTaskService = Depends(_get_task_service),
) -> ApiResponseVO[TranslationTaskStatusVO]:
    """Retrieve persisted translation task status."""
    result = await task_service.get_task_status(request.task_id)
    if result is None:
        raise AppException(
            code=ErrorCode.TASK_NOT_FOUND,
            message=f"Task '{request.task_id}' not found",
            http_status=404,
        )
    return success_response(result)


@router.get(
    "/translation-tasks/{task_id}/file-previews",
    response_model=ApiResponseVO[List[FilePreviewVO]],
    operation_id="get_file_previews",
    responses=common_error_responses(
        ErrorCode.TASK_NOT_FOUND,
        ErrorCode.INTERNAL_ERROR,
    ),
)
async def get_file_previews(
    request: Annotated[
        GetTranslationTaskFilePreviewsRequest,
        Depends(_get_file_previews_request),
    ],
    task_service: TranslationTaskService = Depends(_get_task_service),
) -> ApiResponseVO[List[FilePreviewVO]]:
    """Retrieve translated file preview metadata for a task."""
    result = await task_service.get_file_previews(request.task_id)
    if result is None:
        raise AppException(
            code=ErrorCode.TASK_NOT_FOUND,
            message=f"Task '{request.task_id}' not found",
            http_status=404,
        )
    return success_response(result)
