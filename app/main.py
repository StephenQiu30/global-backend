"""FastAPI application factory."""

from fastapi import FastAPI

from app.controller.installation_controller import router as installations_router
from app.controller.language_controller import router as languages_router
from app.controller.repository_controller import router as repositories_router
from app.controller.translation_task_controller import (
    router as tasks_router,
    _get_task_runner,
)
from app.controller.public_preview_controller import (
    router as public_preview_router,
    _get_public_preview_service,
)
from app.services.task_runner import TaskRunner
from app.services.public_repository import PublicPreviewService

OPENAPI_TAGS = [
    {"name": "installations", "description": "GitHub App installation management"},
    {"name": "repositories", "description": "Repository discovery and authorization"},
    {"name": "languages", "description": "Supported language listing"},
    {"name": "translation-tasks", "description": "Translation task execution"},
    {"name": "public-preview", "description": "Public repository translation preview"},
]


def create_app(
    task_runner: TaskRunner | None = None,
    public_preview_service: PublicPreviewService | None = None,
) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        task_runner: Optional TaskRunner instance (for testing)
        public_preview_service: Optional PublicPreviewService instance (for testing)

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="GitHub Markdown Translator",
        description="Backend API for GitHub Markdown translation",
        version="0.1.0",
        openapi_tags=OPENAPI_TAGS,
    )

    if task_runner is not None:
        app.dependency_overrides[_get_task_runner] = lambda: task_runner

    if public_preview_service is not None:
        app.dependency_overrides[_get_public_preview_service] = (
            lambda: public_preview_service
        )

    app.include_router(installations_router, prefix="/api/github")
    app.include_router(languages_router, prefix="/api")
    app.include_router(repositories_router, prefix="/api")
    app.include_router(tasks_router, prefix="/api")
    app.include_router(public_preview_router, prefix="/api")

    return app


app = create_app()
