"""API endpoints for repository operations."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.domain.markdown_files import validate_selection
from app.services.markdown_discovery import discover_markdown_files, MarkdownFileInfo

router = APIRouter(prefix="/api/repositories", tags=["repositories"])


async def verify_repository_authorization(installation_id: str, owner: str, repo: str) -> bool:
    """Verify repository is authorized for the installation.

    This is a placeholder that will be replaced with actual GitHub API
    verification when GithubAppService is available (after STE-322 merge).

    Args:
        installation_id: GitHub App installation ID
        owner: Repository owner
        repo: Repository name

    Returns:
        True if authorized, False otherwise
    """
    # TODO: Replace with actual GithubAppService.is_repository_authorized call
    # when STE-322 is merged. For now, check that installation_id is provided.
    return bool(installation_id)


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
    # Verify repository authorization
    if not await verify_repository_authorization(installation_id, owner, repo):
        raise HTTPException(
            status_code=404,
            detail={"error": "repository_not_installed", "message": "Repository is not authorized"}
        )

    # Fetch repository tree from GitHub
    # In production, this would call the actual GitHub API via get_repository_tree
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
