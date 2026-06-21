"""DTOs for translation task API endpoints."""

from typing import List

from pydantic import BaseModel, Field


class TranslationTaskCreateDTO(BaseModel):
    """Request DTO for POST /api/translation-tasks."""

    installation_id: str = Field(..., min_length=1)
    repository: str = Field(..., min_length=1)
    base_branch: str = Field(..., min_length=1)
    files: List[str] = Field(..., min_length=1)
    language: str = Field(..., min_length=1)
