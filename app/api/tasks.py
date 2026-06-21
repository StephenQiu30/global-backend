"""Translation task API endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from app.application.translation_task_service import (
    TranslationTaskRequest,
    TranslationTaskService,
    UnsupportedLanguageError,
)
from app.core.errors import AppError
from app.domain.task import TaskResult
from app.dto.translation_task_dto import CreateTranslationTaskDTO
from app.services.task_runner import TaskRunner
from app.vo.translation_task_vo import TranslationTaskVO, FileMappingVO

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


def _to_translation_task_vo(result: TaskResult) -> TranslationTaskVO:
    """Convert domain TaskResult to response VO."""
    return TranslationTaskVO(
        status=result.status.value,
        pr_url=result.pr_url,
        pr_number=result.pr_number,
        mappings=[
            FileMappingVO(source_path=m.source_path, target_path=m.target_path)
            for m in result.mappings
        ]
        if result.mappings
        else None,
        error_code=result.error_code,
        error_message=result.error_message,
    )


def _get_task_runner() -> TaskRunner:
    """Dependency to get TaskRunner. Override in app factory."""
    raise NotImplementedError("TaskRunner not configured")


def _get_translation_task_service(
    task_runner: TaskRunner = Depends(_get_task_runner),
) -> TranslationTaskService:
    """Dependency to get TranslationTaskService."""
    return TranslationTaskService(task_runner=task_runner)


@router.post("/translation-tasks", response_model=TranslationTaskVO)
async def create_translation_task(
    request: CreateTranslationTaskDTO,
    service: TranslationTaskService = Depends(_get_translation_task_service),
) -> TranslationTaskVO:
    """Create and execute a translation task synchronously.

    Args:
        request: Translation task request DTO
        service: Translation task service

    Returns:
        TranslationTaskVO with status, PR info, or error details
    """
    try:
        task_request = TranslationTaskRequest(
            installation_id=request.installation_id,
            repository=request.repository,
            base_branch=request.base_branch,
            files=request.files,
            language=request.language,
        )
        result = await service.create_task(task_request)
        return _to_translation_task_vo(result)
    except UnsupportedLanguageError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "unsupported_language",
                "message": f"Language '{e.language}' is not supported",
            },
        )
