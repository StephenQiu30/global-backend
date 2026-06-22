"""Controller for language listing endpoint."""

from fastapi import APIRouter

from app.core.response import ApiResponseVO, success_response
from app.domain.languages import Language, SUPPORTED_LANGUAGES

router = APIRouter(tags=["languages"])


@router.get(
    "/languages",
    response_model=ApiResponseVO[list[Language]],
    operation_id="get_languages",
)
def get_languages() -> ApiResponseVO[list[Language]]:
    """Get list of supported languages.

    Returns:
        ApiResponseVO containing list of supported Language objects with code and label
    """
    return success_response(SUPPORTED_LANGUAGES)
