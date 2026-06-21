"""Installation API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.application.installation_service import (
    GitHubApiError,
    InstallationNotFoundError,
    InstallationService,
)
from app.core.config import Settings
from app.services.github_app import GitHubAppClient

router = APIRouter()


class VerifyRequest(BaseModel):
    installation_id: int


def get_github_client() -> GitHubAppClient:
    settings = Settings()
    return GitHubAppClient(
        app_id=settings.github_app_id,
        private_key=settings.github_private_key,
    )


def get_installation_service() -> InstallationService:
    return InstallationService(github_client=get_github_client())


@router.post("/installations/verify")
def verify_installation(body: VerifyRequest):
    service = get_installation_service()
    try:
        result = service.verify_installation(body.installation_id)
        return result.model_dump()
    except InstallationNotFoundError:
        raise HTTPException(status_code=404, detail="Installation not found")
    except GitHubApiError:
        raise HTTPException(status_code=502, detail="GitHub API error")


@router.get("/installations/{installation_id}/repositories")
def list_installation_repositories(installation_id: int):
    service = get_installation_service()
    try:
        result = service.list_repositories(installation_id)
        return result.model_dump()
    except InstallationNotFoundError:
        raise HTTPException(status_code=404, detail="Installation not found")
    except GitHubApiError:
        raise HTTPException(status_code=502, detail="GitHub API error")
