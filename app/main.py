import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
import sentry_sdk

from app.api import text_extract  # updated
sentry_sdk.init(
    dsn="https://5c74c0bf64424183a3d8fea7a803a9b0@o4505535984828416.ingest.sentry.io/4505535986335744",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,    
    profiles_sampler=1.0,
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
        contact={
            "name": "Fabio",
        },
        lifespan=lifespan
    )
    application.include_router(text_extract.router)

    return application


app = create_application()
