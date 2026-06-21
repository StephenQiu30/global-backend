"""VOs for repository discovery and authorization responses."""

from pydantic import BaseModel


class ResolveRepositoryVO(BaseModel):
    """Response VO for POST /api/repositories/resolve."""

    full_name: str
    default_branch: str
    private: bool


class MarkdownFileVO(BaseModel):
    """Response VO for a discoverable Markdown file."""

    path: str
    size_bytes: int
    is_default_readme: bool
    is_translated_variant: bool
    disabled_reason: str | None
    target_path_preview: str
    target_exists: bool
