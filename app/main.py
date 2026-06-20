"""FastAPI application factory."""

from fastapi import FastAPI

from app.api.installations import router as installations_router
from app.api.tasks import router as tasks_router, _get_task_runner
from app.services.task_runner import TaskRunner


def create_app(task_runner: TaskRunner | None = None) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        task_runner: Optional TaskRunner instance (for testing)

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="GitHub Markdown Translator",
        description="Backend API for GitHub Markdown translation",
        version="0.1.0",
    )

    if task_runner is not None:
        app.dependency_overrides[_get_task_runner] = lambda: task_runner

    app.include_router(installations_router, prefix="/api/github")
    app.include_router(tasks_router, prefix="/api")

    return app


app = create_app()
