import logging

from fastapi import FastAPI

from backend.app.api.ai import router as ai_router
from backend.app.api.auth import router as auth_router
from backend.app.config.settings import settings
from backend.app.core.logging import setup_logging
from backend.app.api.fees import router as fees_router
from backend.app.api.voice import router as voice_router

setup_logging()

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="Modular AI application backend",
    version=settings.app_version,
    debug=settings.debug,
)

app.include_router(auth_router)
app.include_router(fees_router)
app.include_router(ai_router)
app.include_router(voice_router)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down %s", settings.app_name)


@app.get("/health")
def health_check():
    logger.info("Health check requested")

    return {
        "status": "healthy",
        "service": "xyz-ai-backend",
        "environment": settings.environment,
    }