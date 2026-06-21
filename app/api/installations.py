"""Installation API endpoints."""

from fastapi import APIRouter, HTTPException

from app.application.installation_service import (
    GitHubApiError,
    InstallationNotFoundError,
    InstallationService,
)
from app.core.config import Settings
from app.dto.installation_dto import VerifyInstallationDTO
from app.services.github_app import GitHubAppClient
from app.vo.installation_vo import InstallationVO, RepositoryItemVO, RepositoryListVO

router = APIRouter()


def get_github_client() -> GitHubAppClient:
    settings = Settings()
    return GitHubAppClient(
        app_id=settings.github_app_id,
        private_key=settings.github_private_key,
    )


def get_installation_service() -> InstallationService:
    return InstallationService(github_client=get_github_client())


@router.post("/installations/verify", response_model=InstallationVO)
def verify_installation(body: VerifyInstallationDTO):
    service = get_installation_service()
    try:
        result = service.verify_installation(body.installation_id)
        return InstallationVO(
            installation_id=result.installation_id,
            account_login=result.account_login,
            account_type=result.account_type,
            repository_selection=result.repository_selection,
        )
    except InstallationNotFoundError:
        raise HTTPException(status_code=404, detail="Installation not found")
    except GitHubApiError:
        raise HTTPException(status_code=502, detail="GitHub API error")


@router.get(
    "/installations/{installation_id}/repositories",
    response_model=RepositoryListVO,
)
def list_installation_repositories(installation_id: int):
    service = get_installation_service()
    try:
        result = service.list_repositories(installation_id)
        return RepositoryListVO(
            repositories=[
                RepositoryItemVO(
                    full_name=r.full_name,
                    default_branch=r.default_branch,
                    private=r.private,
                )
                for r in result.repositories
            ]
        )
    except InstallationNotFoundError:
        raise HTTPException(status_code=404, detail="Installation not found")
    except GitHubApiError:
        raise HTTPException(status_code=502, detail="GitHub API error")
