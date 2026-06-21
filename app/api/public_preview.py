"""Public preview API endpoint."""

from fastapi import APIRouter, Depends, HTTPException

from app.dto.translation_task_dto import CreatePublicPreviewDTO
from app.services.public_repository import (
    PublicPreviewService,
    PublicPreviewResult,
)
from app.vo.translation_task_vo import PublicPreviewVO, FilePreviewVO

router = APIRouter()


def _to_public_preview_vo(result: PublicPreviewResult) -> PublicPreviewVO:
    """Convert service PublicPreviewResult to response VO."""
    return PublicPreviewVO(
        previews=[
            FilePreviewVO(
                source_path=p.source_path,
                target_path=p.target_path,
                translated_content=p.translated_content,
            )
            for p in result.previews
        ]
    )


def _get_public_preview_service() -> PublicPreviewService:
    """Dependency to get PublicPreviewService. Override in app factory."""
    raise NotImplementedError("PublicPreviewService not configured")


@router.post("/public-preview", response_model=PublicPreviewVO)
async def create_public_preview(
    request: CreatePublicPreviewDTO,
    service: PublicPreviewService = Depends(_get_public_preview_service),
) -> PublicPreviewVO:
    """Create a read-only translation preview for a public repository.

    Args:
        request: Public preview request DTO
        service: Public preview service

    Returns:
        PublicPreviewVO with translated previews (no PR URL)
    """
    try:
        result = await service.preview(
            repository=request.repository,
            branch="main",
            files=request.files,
            language=request.language,
        )
        return _to_public_preview_vo(result)
    except ValueError as e:
        msg = str(e).lower()
        if "not found" in msg:
            raise HTTPException(
                status_code=404,
                detail={"error_code": "repository_not_found", "message": str(e)},
            )
        if "rate_limited" in msg:
            raise HTTPException(
                status_code=429,
                detail={"error_code": "rate_limited", "message": str(e)},
            )
        if "too many" in msg or "exceeds limit" in msg:
            raise HTTPException(
                status_code=422,
                detail={"error_code": "validation_error", "message": str(e)},
            )
        if "unsafe" in msg or "not supported" in msg or "excluded" in msg:
            raise HTTPException(
                status_code=400,
                detail={"error_code": "validation_error", "message": str(e)},
            )
        raise HTTPException(
            status_code=400,
            detail={"error_code": "validation_error", "message": str(e)},
        )
    except RuntimeError as e:
        msg = str(e).lower()
        if "translat" in msg:
            raise HTTPException(
                status_code=502,
                detail={
                    "error_code": "translation_error",
                    "message": "Translation provider returned an error",
                },
            )
        raise HTTPException(
            status_code=502,
            detail={"error_code": "github_api_error", "message": "GitHub API error"},
        )
