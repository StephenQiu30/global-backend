"""Public preview API endpoint."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.services.public_repository import PublicPreviewService, PublicPreviewResult

router = APIRouter()


class PublicPreviewRequest(BaseModel):
    """Request model for POST /api/public-preview."""

    repository: str = Field(..., min_length=1)
    files: List[str] = Field(..., min_length=1)
    language: str = Field(..., min_length=1)


def _get_public_preview_service() -> PublicPreviewService:
    """Dependency to get PublicPreviewService. Override in app factory."""
    raise NotImplementedError("PublicPreviewService not configured")


@router.post("/public-preview", response_model=PublicPreviewResult)
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
            raise HTTPException(status_code=404, detail=str(e))
        if "rate_limited" in msg:
            raise HTTPException(status_code=429, detail=str(e))
        if "unsafe" in msg or "not supported" in msg or "excluded" in msg:
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError:
        raise HTTPException(status_code=502, detail="GitHub API error")
