"""Controller for GitHub App installation endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import Settings
from app.services.github_app import GitHubAppClient

router = APIRouter(prefix="/installations", tags=["installations"])


class VerifyRequest(BaseModel):
    """Request body for installation verification."""

    installation_id: int


class InstallationResponse(BaseModel):
    """Response body for a verified installation."""

    installation_id: int
    account_login: str
    account_type: str
    repository_selection: str


class RepositoryItem(BaseModel):
    """A single repository in an installation."""

    full_name: str
    default_branch: str
    private: bool


class RepositoryListResponse(BaseModel):
    """Response body listing installation repositories."""

    repositories: list[RepositoryItem]


class ErrorResponse(BaseModel):
    """Structured error response."""

    error: str


def get_github_client() -> GitHubAppClient:
    """Create a GitHubAppClient from current settings."""
    settings = Settings()
    return GitHubAppClient(
        app_id=settings.github_app_id,
        private_key=settings.github_private_key,
    )


@router.post(
    "/verify",
    response_model=InstallationResponse,
    operation_id="verify_installation",
    responses={
        404: {"model": ErrorResponse, "description": "Installation not found"},
        502: {"model": ErrorResponse, "description": "GitHub API error"},
    },
)
def verify_installation(body: VerifyRequest) -> InstallationResponse:
    """Verify a GitHub App installation exists and is accessible."""
    client = get_github_client()
    try:
        info = client.get_installation(body.installation_id)
        return InstallationResponse(
            installation_id=info.installation_id,
            account_login=info.account_login,
            account_type=info.account_type,
            repository_selection=info.repository_selection,
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Installation not found")
    except RuntimeError:
        raise HTTPException(status_code=502, detail="GitHub API error")


@router.get(
    "/{installation_id}/repositories",
    response_model=RepositoryListResponse,
    operation_id="list_installation_repositories",
    responses={
        404: {"model": ErrorResponse, "description": "Installation not found"},
        502: {"model": ErrorResponse, "description": "GitHub API error"},
    },
)
def list_installation_repositories(installation_id: int) -> RepositoryListResponse:
    """List repositories accessible by a GitHub App installation."""
    client = get_github_client()
    try:
        repos = client.get_installation_repos(installation_id)
        return RepositoryListResponse(
            repositories=[
                RepositoryItem(
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
