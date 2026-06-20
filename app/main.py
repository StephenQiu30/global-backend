from fastapi import FastAPI

from app.api.installations import router as installations_router


def create_app() -> FastAPI:
    app = FastAPI(title="global-backend", version="0.1.0")
    app.include_router(installations_router, prefix="/api/github")
    return app
