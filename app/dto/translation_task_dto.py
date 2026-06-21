"""DTOs for translation task and public preview endpoints."""

from pydantic import BaseModel, Field


class CreateTranslationTaskDTO(BaseModel):
    """Request DTO for POST /api/translation-tasks."""

    installation_id: str = Field(..., min_length=1)
    repository: str = Field(..., min_length=1)
    base_branch: str = Field(..., min_length=1)
    files: list[str] = Field(..., min_length=1)
    language: str = Field(..., min_length=1)


class CreatePublicPreviewDTO(BaseModel):
    """Request DTO for POST /api/public-preview."""

    repository: str = Field(..., min_length=1)
    files: list[str] = Field(..., min_length=1)
    language: str = Field(..., min_length=1)
