"""Translation task API endpoints."""

from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.domain.task import TaskResult
from app.services.task_runner import TaskRunner

router = APIRouter()


class TranslationTaskRequest(BaseModel):
    """Request model for POST /api/translation-tasks."""

    installation_id: str = Field(..., min_length=1)
    repository: str = Field(..., min_length=1)
    base_branch: str = Field(..., min_length=1)
    files: List[str] = Field(..., min_length=1)
    language: str = Field(..., min_length=1)


def _get_task_runner() -> TaskRunner:
    """Dependency to get TaskRunner. Override in app factory."""
    raise NotImplementedError("TaskRunner not configured")


@router.post("/translation-tasks", response_model=TaskResult)
async def create_translation_task(
    request: TranslationTaskRequest,
    task_runner: TaskRunner = Depends(_get_task_runner),
) -> TaskResult:
    """Create and execute a translation task synchronously.

    Args:
        request: Translation task request
        task_runner: Task runner service

    Returns:
        TaskResult with status, PR info, or error details
    """
    from app.domain.task import Task

    task = Task(
        task_id="generated",
        installation_id=request.installation_id,
        repository=request.repository,
        base_branch=request.base_branch,
        files=request.files,
        language=request.language,
    )
    return await task_runner.run(task)
