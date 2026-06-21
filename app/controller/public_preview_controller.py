"""Controller for public repository preview endpoint."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.services.public_repository import PublicPreviewService, PublicPreviewResult

router = APIRouter(tags=["public-preview"])


class PublicPreviewRequest(BaseModel):
    """Request model for POST /api/public-preview."""

    repository: str = Field(..., min_length=1)
    files: List[str] = Field(..., min_length=1)
    language: str = Field(..., min_length=1)


class ErrorResponse(BaseModel):
    """Structured error response."""

    error_code: str
    message: str


def _get_public_preview_service() -> PublicPreviewService:
    """Dependency to get PublicPreviewService. Override in app factory."""
    raise NotImplementedError("PublicPreviewService not configured")


@router.post(
    "/public-preview",
    response_model=PublicPreviewResult,
    operation_id="create_public_preview",
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        404: {"model": ErrorResponse, "description": "Repository not found"},
        429: {"model": ErrorResponse, "description": "Rate limited"},
        502: {"model": ErrorResponse, "description": "Translation or GitHub error"},
    },
)
async def create_public_preview(
    request: PublicPreviewRequest,
    service: PublicPreviewService = Depends(_get_public_preview_service),
) -> PublicPreviewResult:
    """Create a read-only translation preview for a public repository.

    Args:
        request: Public preview request
        service: Public preview service

    Returns:
        PublicPreviewResult with translated previews (no PR URL)
    """
    try:
        return await service.preview(
            repository=request.repository,
            branch="main",
            files=request.files,
            language=request.language,
        )
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
