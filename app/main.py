"""FastAPI application factory."""

from fastapi import FastAPI

from app.api.installations import router as installations_router
from app.api.languages import router as languages_router
from app.api.repositories import router as repositories_router
from app.api.tasks import router as tasks_router, _get_task_service
from app.api.public_preview import (
    router as public_preview_router,
    _get_public_preview_service,
)
from app.services.public_repository import PublicPreviewService
from app.services.translation_task_service import TranslationTaskService


def create_app(
    task_service: TranslationTaskService | None = None,
    public_preview_service: PublicPreviewService | None = None,
) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        task_service: Optional TranslationTaskService instance (for testing)
        public_preview_service: Optional PublicPreviewService instance (for testing)

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="GitHub Markdown Translator",
        description="Backend API for GitHub Markdown translation",
        version="0.1.0",
    )

    if task_service is not None:
        app.dependency_overrides[_get_task_service] = lambda: task_service

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
