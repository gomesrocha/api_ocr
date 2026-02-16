import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
import sentry_sdk

from app.api import text_extract
from app.config import get_settings

settings = get_settings()

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        profiles_sampler=1.0,
        environment=settings.environment,
    )

log = logging.getLogger("uvicorn")

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting up...")
    yield
    log.info("Shutting down...")

def create_application() -> FastAPI:
    application = FastAPI(
        title="API_OCR",
        version="0.1.0",
        description="OCR API project using tesseract and fastapi",
        author="Fabio",
        lifespan=lifespan
    )
    application.include_router(text_extract.router)
    return application


app = create_application()
