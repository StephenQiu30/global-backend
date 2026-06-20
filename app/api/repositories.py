"""API endpoints for repository operations."""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.domain.repository import parse_repository_input
from app.services.github_app import GithubAppService

router = APIRouter(prefix="/repositories", tags=["repositories"])

github_service = GithubAppService()


class ResolveRequest(BaseModel):
    """Request body for repository resolve."""

    input: str
    installation_id: int


class ResolveResponse(BaseModel):
    """Response body for successful repository resolve."""

    full_name: str
    default_branch: str
    private: bool


class ErrorResponse(BaseModel):
    """Response body for errors."""

    error: str


@router.post(
    "/resolve",
    response_model=ResolveResponse,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
    },
)
async def resolve_repository(request: ResolveRequest) -> dict[str, Any]:
    """Parse and verify repository authorization.

    Parses the repository input, then checks if the repository
    is authorized for the given GitHub App installation.
    """
    try:
        ref = parse_repository_input(request.input)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={"error": "invalid_repository_url"},
        )

    is_authorized = await github_service.is_repository_authorized(
        installation_id=request.installation_id,
        full_name=ref.full_name,
    )

    if not is_authorized:
        raise HTTPException(
            status_code=403,
            detail={"error": "repository_not_installed"},
        )

    return {
        "full_name": ref.full_name,
        "default_branch": "main",
        "private": True,
    }
