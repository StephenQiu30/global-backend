"""API endpoints for repository operations."""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.installations import get_github_client
from app.domain.repository import parse_repository_input

router = APIRouter(prefix="/repositories", tags=["repositories"])


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
def resolve_repository(request: ResolveRequest) -> dict[str, Any]:
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

    client = get_github_client()
    try:
        is_authorized = client.is_repository_authorized(
            installation_id=request.installation_id,
            full_name=ref.full_name,
        )
    except RuntimeError:
        raise HTTPException(
            status_code=502,
            detail={"error": "github_api_error"},
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
