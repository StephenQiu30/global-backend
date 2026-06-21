"""Controller for public repository preview endpoint."""

from fastapi import APIRouter, Depends

from app.core.response import ApiResponseVO, success_response
from app.dto.translation_task import CreatePublicPreviewRequest
from app.services.public_repository import PublicPreviewService, PublicPreviewResult
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
    response_model=ApiResponseVO[PublicPreviewVO],
    operation_id="create_public_preview",
)
async def create_public_preview(
    request: CreatePublicPreviewRequest,
    service: PublicPreviewService = Depends(_get_public_preview_service),
) -> ApiResponseVO[PublicPreviewVO]:
    """Create a read-only translation preview for a public repository."""
    result = await service.preview(
        repository=request.repository,
        branch="main",
        files=request.files,
        language=request.language,
    )
    return success_response(_to_public_preview_vo(result))
