from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers.health import router as health_router
from app.routers.transcribe import router as transcribe_router
from app.utils.logging import setup_logging


def create_app() -> FastAPI:
    app = FastAPI(title="Audio Transcriber API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(transcribe_router)
    return app


setup_logging()

app = create_app()


