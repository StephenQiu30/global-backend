"""Controller for GitHub App installation endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.github import get_github_client
from app.core.openapi import common_error_responses
from app.core.response import ErrorCode, success_response, ApiResponseVO
from app.dto.installation import (
    ListInstallationRepositoriesRequest,
    VerifyInstallationRequest,
)
from app.services.installation_service import InstallationService
from app.vo.installation_vo import (
    InstallationVO,
    RepositoryItemVO,
    RepositoryListVO,
)

router = APIRouter(prefix="/installations", tags=["installations"])


def _get_installation_service() -> InstallationService:
    """Dependency to get InstallationService. Override in app factory."""
    raise NotImplementedError("InstallationService not configured")


def _list_installation_repositories_request(
    installation_id: int,
) -> ListInstallationRepositoriesRequest:
    return ListInstallationRepositoriesRequest(installation_id=installation_id)


@router.post(
    "/verify",
    response_model=ApiResponseVO[InstallationVO],
    operation_id="verify_installation",
    responses=common_error_responses(
        ErrorCode.VALIDATION_ERROR,
        ErrorCode.GITHUB_API_ERROR,
        ErrorCode.INSTALLATION_NOT_FOUND,
        ErrorCode.INTERNAL_ERROR,
    ),
)
async def verify_installation(
    body: VerifyInstallationRequest,
    installation_service: InstallationService = Depends(_get_installation_service),
) -> ApiResponseVO[InstallationVO]:
    """Verify a GitHub App installation and persist account metadata."""
    client = get_github_client()
    info = client.get_installation(body.installation_id)

    await installation_service.verify_and_persist(
        installation_id=info.installation_id,
        account_login=info.account_login,
        account_type=info.account_type,
    )

    return success_response(InstallationVO(
        installation_id=info.installation_id,
        account_login=info.account_login,
        account_type=info.account_type,
        repository_selection=info.repository_selection,
    ))


@router.get(
    "/{installation_id}/repositories",
    response_model=ApiResponseVO[RepositoryListVO],
    operation_id="list_installation_repositories",
    responses=common_error_responses(
        ErrorCode.GITHUB_API_ERROR,
        ErrorCode.INSTALLATION_NOT_FOUND,
        ErrorCode.INTERNAL_ERROR,
    ),
)
def list_installation_repositories(
    request: Annotated[
        ListInstallationRepositoriesRequest,
        Depends(_list_installation_repositories_request),
    ],
) -> ApiResponseVO[RepositoryListVO]:
    """List repositories accessible by a GitHub App installation."""
    client = get_github_client()
    repos = client.get_installation_repos(request.installation_id)
    return success_response(RepositoryListVO(
        repositories=[
            RepositoryItemVO(
                full_name=r.full_name,
                default_branch=r.default_branch,
                private=r.private,
            )
            for r in repos
        ]
    ))
