"""Controller for GitHub App installation endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.core.github import get_github_client
from app.dto.installation import (
    ListInstallationRepositoriesRequest,
    VerifyInstallationRequest,
)
from app.services.installation_service import InstallationService
from app.vo.error_vo import SimpleErrorVO
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
    response_model=InstallationVO,
    operation_id="verify_installation",
    responses={
        404: {"model": SimpleErrorVO, "description": "Installation not found"},
        502: {"model": SimpleErrorVO, "description": "GitHub API error"},
    },
)
async def verify_installation(
    body: VerifyInstallationRequest,
    installation_service: InstallationService = Depends(_get_installation_service),
) -> InstallationVO:
    """Verify a GitHub App installation and persist account metadata."""
    client = get_github_client()
    try:
        info = client.get_installation(body.installation_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Installation not found")
    except RuntimeError:
        raise HTTPException(status_code=502, detail="GitHub API error")

    await installation_service.verify_and_persist(
        installation_id=info.installation_id,
        account_login=info.account_login,
        account_type=info.account_type,
    )

    return InstallationVO(
        installation_id=info.installation_id,
        account_login=info.account_login,
        account_type=info.account_type,
        repository_selection=info.repository_selection,
    )


@router.get(
    "/{installation_id}/repositories",
    response_model=RepositoryListVO,
    operation_id="list_installation_repositories",
    responses={
        404: {"model": SimpleErrorVO, "description": "Installation not found"},
        502: {"model": SimpleErrorVO, "description": "GitHub API error"},
    },
)
def list_installation_repositories(
    request: Annotated[
        ListInstallationRepositoriesRequest,
        Depends(_list_installation_repositories_request),
    ],
) -> RepositoryListVO:
    """List repositories accessible by a GitHub App installation."""
    client = get_github_client()
    try:
        repos = client.get_installation_repos(request.installation_id)
        return RepositoryListVO(
            repositories=[
                RepositoryItemVO(
                    full_name=r.full_name,
                    default_branch=r.default_branch,
                    private=r.private,
                )
                for r in repos
            ]
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Installation not found")
    except RuntimeError:
        raise HTTPException(status_code=502, detail="GitHub API error")
