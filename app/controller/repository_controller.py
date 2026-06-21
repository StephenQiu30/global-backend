"""Controller for repository discovery and authorization endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.core.github import get_github_client
from app.domain.markdown_files import validate_selection
from app.domain.repository import parse_repository_input
from app.dto.repository import (
    GetMarkdownFilesRequest,
    ResolveRepositoryRequest,
)
from app.services.markdown_discovery import (
    discover_markdown_files,
    get_repository_tree,
)
from app.vo.error_vo import SimpleErrorVO
from app.vo.repository_vo import MarkdownFileVO, ResolveRepositoryVO

router = APIRouter(prefix="/repositories", tags=["repositories"])


@router.post(
    "/resolve",
    response_model=ResolveRepositoryVO,
    operation_id="resolve_repository",
    responses={
        400: {"model": SimpleErrorVO, "description": "Invalid repository URL"},
        403: {"model": SimpleErrorVO, "description": "Repository not installed"},
        502: {"model": SimpleErrorVO, "description": "GitHub API error"},
    },
)
def resolve_repository(request: ResolveRepositoryRequest) -> ResolveRepositoryVO:
    """Parse and verify repository authorization."""
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

    return ResolveRepositoryVO(
        full_name=ref.full_name,
        default_branch=default_branch,
        private=repo_info.private if repo_info else True,
    )


@router.get(
    "/{owner}/{repo}/markdown-files",
    response_model=list[MarkdownFileVO],
    operation_id="get_markdown_files",
    responses={
        400: {"model": SimpleErrorVO, "description": "Invalid parameters"},
        404: {"model": SimpleErrorVO, "description": "Repository not found"},
        502: {"model": SimpleErrorVO, "description": "GitHub API error"},
    },
)
async def get_markdown_files(
    owner: str,
    repo: str,
    request: Annotated[GetMarkdownFilesRequest, Query()],
) -> list[MarkdownFileVO]:
    """Get eligible Markdown files for a repository."""
    if request.installation_id is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "repository_not_installed",
                "message": "Repository is not authorized",
            },
        )

    try:
        parsed_installation_id = int(request.installation_id)
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
            detail={"error": "repository_not_installed", "message": "Repository is not authorized"},
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

    files = discover_markdown_files(tree_items, language=request.language)

    file_vos = [
        MarkdownFileVO(
            path=f.path,
            size_bytes=f.size_bytes,
            is_default_readme=f.is_default_readme,
            is_translated_variant=f.is_translated_variant,
            disabled_reason=f.disabled_reason,
            target_path_preview=f.target_path_preview,
            target_exists=f.target_exists,
        )
        for f in files
    ]

    validation_error = validate_selection([vo.model_dump() for vo in file_vos])
    if validation_error:
        raise HTTPException(
            status_code=400,
            detail={"error": "selection_limit_exceeded", "message": validation_error},
        )

    return file_vos
