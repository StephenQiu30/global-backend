"""Controller for public repository preview endpoint."""

from fastapi import APIRouter, Depends, HTTPException

from app.dto.translation_task import CreatePublicPreviewRequest
from app.services.public_repository import PublicPreviewService, PublicPreviewResult
from app.vo.error_vo import CodeMessageErrorVO
from app.vo.translation_task_vo import FilePreviewVO, PublicPreviewVO

router = APIRouter(tags=["public-preview"])


def _get_public_preview_service() -> PublicPreviewService:
    """Dependency to get PublicPreviewService. Override in app factory."""
    raise NotImplementedError("PublicPreviewService not configured")


def _to_public_preview_vo(result: PublicPreviewResult) -> PublicPreviewVO:
    """Map service result to API response VO."""
    return PublicPreviewVO(
        previews=[
            FilePreviewVO(
                source_path=preview.source_path,
                target_path=preview.target_path,
                translated_content=preview.translated_content,
                status="translated",
            )
            for preview in result.previews
        ]
    )


@router.post(
    "/public-preview",
    response_model=PublicPreviewVO,
    operation_id="create_public_preview",
    responses={
        400: {"model": CodeMessageErrorVO, "description": "Validation error"},
        404: {"model": CodeMessageErrorVO, "description": "Repository not found"},
        429: {"model": CodeMessageErrorVO, "description": "Rate limited"},
        502: {"model": CodeMessageErrorVO, "description": "Translation or GitHub error"},
    },
)
async def create_public_preview(
    request: CreatePublicPreviewRequest,
    service: PublicPreviewService = Depends(_get_public_preview_service),
) -> PublicPreviewVO:
    """Create a read-only translation preview for a public repository."""
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
