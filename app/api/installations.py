from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import Settings
from app.services.github_app import GitHubAppClient

router = APIRouter()


class VerifyRequest(BaseModel):
    installation_id: int


class InstallationResponse(BaseModel):
    installation_id: int
    account_login: str
    account_type: str
    repository_selection: str


class RepositoryItem(BaseModel):
    full_name: str
    default_branch: str
    private: bool


class RepositoryListResponse(BaseModel):
    repositories: list[RepositoryItem]


def get_github_client() -> GitHubAppClient:
    settings = Settings()
    return GitHubAppClient(
        app_id=settings.github_app_id,
        private_key=settings.github_private_key,
    )


@router.post("/installations/verify", response_model=InstallationResponse)
def verify_installation(body: VerifyRequest):
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
    "/installations/{installation_id}/repositories",
    response_model=RepositoryListResponse,
)
def list_installation_repositories(installation_id: int):
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
