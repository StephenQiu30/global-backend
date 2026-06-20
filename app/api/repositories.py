"""API endpoints for repository operations."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.services.markdown_discovery import discover_markdown_files, MarkdownFileInfo

router = APIRouter(prefix="/api/repositories", tags=["repositories"])


@router.get("/{owner}/{repo}/markdown-files")
async def get_markdown_files(
    owner: str,
    repo: str,
    language: str = Query(default="zh-CN", description="Target language for path previews"),
    installation_id: Optional[str] = None,
) -> list[dict]:
    """Get eligible Markdown files for a repository.

    Args:
        owner: Repository owner
        repo: Repository name
        language: Target language for path previews (default: zh-CN)
        installation_id: GitHub App installation ID (from request context)

    Returns:
        List of eligible Markdown files with metadata

    Raises:
        HTTPException: If repository is not authorized
    """
    # In production, installation_id would come from request context
    # For now, we require it as a parameter for testing
    if not installation_id:
        raise HTTPException(
            status_code=404,
            detail={"error": "repository_not_installed", "message": "Repository is not authorized"}
        )

    # Fetch repository tree from GitHub
    # In production, this would call the actual GitHub API
    tree_items = []  # Would be fetched from GitHub

    # Discover eligible Markdown files
    files = discover_markdown_files(tree_items, language=language)

    # Convert to response format
    return [
        {
            "path": f.path,
            "size_bytes": f.size_bytes,
            "is_default_readme": f.is_default_readme,
            "is_translated_variant": f.is_translated_variant,
            "disabled_reason": f.disabled_reason,
            "target_path_preview": f.target_path_preview,
            "target_exists": f.target_exists,
        }
        for f in files
    ]
