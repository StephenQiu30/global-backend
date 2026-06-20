"""API endpoints for language operations."""

from fastapi import APIRouter

from app.domain.languages import Language, SUPPORTED_LANGUAGES

router = APIRouter(tags=["languages"])


@router.get("/languages", response_model=list[Language])
def get_languages() -> list[Language]:
    """Get list of supported languages.

    Returns:
        List of supported Language objects with code and label
    """
    return SUPPORTED_LANGUAGES
