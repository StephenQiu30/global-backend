"""Controller for repository discovery and authorization endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.exceptions import AppException
from app.core.github import get_github_client
from app.core.openapi import common_error_responses
from app.core.response import ErrorCode, ApiResponseVO, success_response
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
from app.vo.repository_vo import MarkdownFileVO, ResolveRepositoryVO

router = APIRouter(prefix="/repositories", tags=["repositories"])


@router.post(
    "/resolve",
    response_model=ApiResponseVO[ResolveRepositoryVO],
    operation_id="resolve_repository",
    responses=common_error_responses(
        ErrorCode.VALIDATION_ERROR,
        ErrorCode.REPOSITORY_NOT_INSTALLED,
        ErrorCode.GITHUB_API_ERROR,
        ErrorCode.INTERNAL_ERROR,
    ),
)
def resolve_repository(request: ResolveRepositoryRequest) -> ApiResponseVO[ResolveRepositoryVO]:
    """Parse and verify repository authorization."""
    try:
        ref = parse_repository_input(request.input)
    except ValueError as err:
        raise AppException(
            code=ErrorCode.VALIDATION_ERROR,
            message="Invalid repository URL",
            http_status=400,
        ) from err

    client = get_github_client()
    is_authorized = client.is_repository_authorized(
        installation_id=request.installation_id,
        full_name=ref.full_name,
    )

    if not is_authorized:
        raise AppException(
            code=ErrorCode.REPOSITORY_NOT_INSTALLED,
            message="Repository is not authorized",
            http_status=403,
        )

    repo_info = client.get_repository_info(
        installation_id=request.installation_id,
        full_name=ref.full_name,
    )
    default_branch = repo_info.default_branch if repo_info else "main"

    return success_response(ResolveRepositoryVO(
        full_name=ref.full_name,
        default_branch=default_branch,
        private=repo_info.private if repo_info else True,
    ))


@router.get(
    "/{owner}/{repo}/markdown-files",
    response_model=ApiResponseVO[list[MarkdownFileVO]],
    operation_id="get_markdown_files",
    responses=common_error_responses(
        ErrorCode.VALIDATION_ERROR,
        ErrorCode.REPOSITORY_NOT_INSTALLED,
        ErrorCode.GITHUB_API_ERROR,
        ErrorCode.INTERNAL_ERROR,
    ),
)
async def get_markdown_files(
    owner: str,
    repo: str,
    request: Annotated[GetMarkdownFilesRequest, Query()],
) -> ApiResponseVO[list[MarkdownFileVO]]:
    """Get eligible Markdown files for a repository."""
    if request.installation_id is None:
        raise AppException(
            code=ErrorCode.REPOSITORY_NOT_INSTALLED,
            message="Repository is not authorized",
            http_status=404,
        )

    try:
        parsed_installation_id = int(request.installation_id)
    except ValueError as err:
        raise AppException(
            code=ErrorCode.VALIDATION_ERROR,
            message="Invalid installation_id",
            http_status=422,
        ) from err

    client = get_github_client()
    is_authorized = client.is_repository_authorized(
        installation_id=parsed_installation_id,
        full_name=f"{owner}/{repo}",
    )

    if not is_authorized:
        raise AppException(
            code=ErrorCode.REPOSITORY_NOT_INSTALLED,
            message="Repository is not authorized",
            http_status=404,
        )

    repo_info = client.get_repository_info(parsed_installation_id, f"{owner}/{repo}")
    branch = repo_info.default_branch if repo_info else "main"

    tree_items = get_repository_tree(
        owner=owner,
        repo=repo,
        branch=branch,
        installation_id=parsed_installation_id,
        github_client=client,
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
        raise AppException(
            code=ErrorCode.VALIDATION_ERROR,
            message=validation_error,
            http_status=422,
        )

    return success_response(file_vos)
