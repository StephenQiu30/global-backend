from fastapi import FastAPI

from app.api.repositories import router as repositories_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="GitHub Markdown Translator",
        description="Backend API for GitHub Markdown translation",
        version="0.1.0",
    )

    app.include_router(repositories_router, prefix="/api")

    return app


app = create_app()
