"""Request DTOs for repository endpoints."""

from pydantic import BaseModel, Field


class ResolveRepositoryRequest(BaseModel):
    """Request body for POST /api/repositories/resolve."""

    input: str = Field(..., description="Repository URL or owner/repo string")
    installation_id: int = Field(..., description="GitHub App installation ID")


class GetMarkdownFilesRequest(BaseModel):
    """Query parameters for GET /api/repositories/{owner}/{repo}/markdown-files."""

    language: str = Field(
        default="zh-CN",
        description="Target language code for translated path previews",
    )
    installation_id: str | None = Field(
        default=None,
        description="GitHub App installation ID",
    )
