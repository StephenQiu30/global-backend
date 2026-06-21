"""API endpoints for repository operations."""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.api.installations import get_github_client
from app.domain.markdown_files import validate_selection
from app.domain.repository import parse_repository_input
from app.services.markdown_discovery import (
    discover_markdown_files,
    get_repository_tree,
)

router = APIRouter(prefix="/repositories", tags=["repositories"])


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
def resolve_repository(request: ResolveRequest) -> dict[str, Any]:
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

    client = get_github_client()
    try:
        is_authorized = client.is_repository_authorized(
            installation_id=request.installation_id,
            full_name=ref.full_name,
        )
    except RuntimeError:
        raise HTTPException(
            status_code=502,
            detail={"error": "github_api_error"},
        )

    if not is_authorized:
        raise HTTPException(
            status_code=403,
            detail={"error": "repository_not_installed"},
        )

    repo_info = client.get_repository_info(
        installation_id=request.installation_id,
        full_name=ref.full_name,
    )
    default_branch = repo_info.default_branch if repo_info else "main"

    return {
        "full_name": ref.full_name,
        "default_branch": default_branch,
        "private": repo_info.private if repo_info else True,
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
        HTTPException: If repository is not authorized or selection limits exceeded
    """
    if installation_id is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "repository_not_installed",
                "message": "Repository is not authorized",
            },
        )

    try:
        parsed_installation_id = int(installation_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail={"error": "invalid_installation_id", "message": "installation_id must be an integer"},
        )

    client = get_github_client()
    is_authorized = client.is_repository_authorized(
        installation_id=parsed_installation_id,
        full_name=f"{owner}/{repo}",
    )

    if not is_authorized:
        raise HTTPException(
            status_code=404,
            detail={"error": "repository_not_installed", "message": "Repository is not authorized"}
        )

    repo_info = client.get_repository_info(parsed_installation_id, f"{owner}/{repo}")
    branch = repo_info.default_branch if repo_info else "main"

    try:
        tree_items = get_repository_tree(
            owner=owner,
            repo=repo,
            branch=branch,
            installation_id=parsed_installation_id,
            github_client=client,
        )
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail={"error": "repository_not_found", "message": "Repository tree not found"},
        )
    except RuntimeError:
        raise HTTPException(
            status_code=502,
            detail={"error": "github_api_error", "message": "GitHub API error"},
        )

    files = discover_markdown_files(tree_items, language=language)

    # Convert to dict format for validation
    file_dicts = [
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

    # Validate selection limits (even though this is a discovery endpoint,
    # we validate to ensure the response is consistent with limits)
    validation_error = validate_selection(file_dicts)
    if validation_error:
        raise HTTPException(
            status_code=400,
            detail={"error": "selection_limit_exceeded", "message": validation_error}
        )

    return file_dicts
