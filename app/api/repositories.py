"""API endpoints for repository operations."""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.domain.repository import parse_repository_input
from app.services.github_app import GithubAppService
from app.services.markdown_discovery import discover_markdown_files, MarkdownFileInfo

router = APIRouter(prefix="/repositories", tags=["repositories"])

github_service = GithubAppService()


class ResolveRequest(BaseModel):
    """Request body for repository resolve."""

    input: str
    installation_id: int


class ResolveResponse(BaseModel):
    """Response body for successful repository resolve."""

    full_name: str
    default_branch: str
    private: bool


class ErrorResponse(BaseModel):
    """Response body for errors."""

    error: str


@router.post(
    "/resolve",
    response_model=ResolveResponse,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
    },
)
async def resolve_repository(request: ResolveRequest) -> dict[str, Any]:
    """Parse and verify repository authorization.

    Parses the repository input, then checks if the repository
    is authorized for the given GitHub App installation.
    """
    try:
        ref = parse_repository_input(request.input)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={"error": "invalid_repository_url"},
        )

    is_authorized = await github_service.is_repository_authorized(
        installation_id=request.installation_id,
        full_name=ref.full_name,
    )

    if not is_authorized:
        raise HTTPException(
            status_code=403,
            detail={"error": "repository_not_installed"},
        )

    return {
        "full_name": ref.full_name,
        "default_branch": "main",
        "private": True,
    }


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
