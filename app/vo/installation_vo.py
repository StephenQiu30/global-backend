"""VOs for installation verification and repository listing responses."""

from pydantic import BaseModel


class InstallationVO(BaseModel):
    """Response VO for POST /api/github/installations/verify."""

    installation_id: int
    account_login: str
    account_type: str
    repository_selection: str


class RepositoryItemVO(BaseModel):
    """Response VO for a single repository in a listing."""

    full_name: str
    default_branch: str
    private: bool


class RepositoryListVO(BaseModel):
    """Response VO for GET /api/github/installations/{id}/repositories."""

    repositories: list[RepositoryItemVO]
