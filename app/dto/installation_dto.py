"""DTOs for installation verification endpoints."""

from pydantic import BaseModel


class VerifyInstallationDTO(BaseModel):
    """Request DTO for POST /api/github/installations/verify."""

    installation_id: int
