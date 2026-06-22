"""Controller for language listing endpoint."""

from fastapi import APIRouter

from app.core.openapi import common_error_responses
from app.core.response import ErrorCode, ApiResponseVO, success_response
from app.domain.languages import Language, SUPPORTED_LANGUAGES

router = APIRouter(tags=["languages"])


@router.get(
    "/languages",
    response_model=ApiResponseVO[list[Language]],
    operation_id="get_languages",
    responses=common_error_responses(ErrorCode.INTERNAL_ERROR),
)
def get_languages() -> ApiResponseVO[list[Language]]:
    """Get list of supported languages.

    Returns:
        ApiResponseVO containing list of supported Language objects with code and label
    """
    return success_response(SUPPORTED_LANGUAGES)
