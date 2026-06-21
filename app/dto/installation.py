"""Request DTOs for installation endpoints."""

from pydantic import BaseModel, Field


class VerifyInstallationRequest(BaseModel):
    """Request body for POST /api/github/installations/verify."""

    installation_id: int = Field(..., description="GitHub App installation ID")


class ListInstallationRepositoriesRequest(BaseModel):
    """Path parameters for GET /api/github/installations/{installation_id}/repositories."""

    installation_id: int = Field(..., description="GitHub App installation ID")
