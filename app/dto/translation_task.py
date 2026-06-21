"""Request DTOs for translation task and public preview endpoints."""

from pydantic import BaseModel, Field


class CreateTranslationTaskRequest(BaseModel):
    """Request body for POST /api/translation-tasks."""

    installation_id: str = Field(..., min_length=1, description="GitHub App installation ID")
    repository: str = Field(..., min_length=1, description="Repository full name owner/repo")
    base_branch: str = Field(..., min_length=1, description="Base branch to translate from")
    files: list[str] = Field(..., min_length=1, description="Markdown file paths to translate")
    language: str = Field(..., min_length=1, description="Target language code")


class CreatePublicPreviewRequest(BaseModel):
    """Request body for POST /api/public-preview."""

    repository: str = Field(..., min_length=1, description="Public repository full name owner/repo")
    files: list[str] = Field(..., min_length=1, description="Markdown file paths to preview")
    language: str = Field(..., min_length=1, description="Target language code")


class GetTranslationTaskStatusRequest(BaseModel):
    """Path parameters for GET /api/translation-tasks/{task_id}."""

    task_id: str = Field(..., description="Translation task ID")


class GetTranslationTaskFilePreviewsRequest(BaseModel):
    """Path parameters for GET /api/translation-tasks/{task_id}/file-previews."""

    task_id: str = Field(..., description="Translation task ID")
