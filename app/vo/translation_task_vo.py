"""VOs for translation task and public preview responses."""

from typing import Optional

from pydantic import BaseModel


class FileMappingVO(BaseModel):
    """Response VO for a source-to-target file mapping."""

    source_path: str
    target_path: str


class TranslationTaskVO(BaseModel):
    """Response VO for POST /api/translation-tasks."""

    status: str
    pr_url: Optional[str] = None
    pr_number: Optional[int] = None
    mappings: Optional[list[FileMappingVO]] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class FilePreviewVO(BaseModel):
    """Response VO for a single translated file preview."""

    source_path: str
    target_path: str
    translated_content: str


class PublicPreviewVO(BaseModel):
    """Response VO for POST /api/public-preview."""

    previews: list[FilePreviewVO]
