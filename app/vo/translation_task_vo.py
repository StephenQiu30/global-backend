"""VOs for translation task and public preview responses."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class TranslationTaskCreateVO(BaseModel):
    """Response VO for POST /api/translation-tasks (async queue dispatch)."""

    task_id: str
    status: str


class TranslationTaskStatusVO(BaseModel):
    """Response VO for GET /api/translation-tasks/{task_id}."""

    task_id: str
    status: str
    repository: str
    language: str
    pr_url: Optional[str] = None
    pr_number: Optional[int] = None
    file_mappings: Optional[List[Dict[str, Any]]] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    created_at: str
    updated_at: str


class FilePreviewVO(BaseModel):
    """Response VO for translated file preview metadata."""

    source_path: str
    target_path: str
    status: str = "translated"
    translated_content: Optional[str] = None


class TaskNotFoundVO(BaseModel):
    """Error response VO for unknown task IDs."""

    error: str = "task_not_found"
    message: str


class PublicPreviewVO(BaseModel):
    """Response VO for POST /api/public-preview."""

    previews: list[FilePreviewVO]
