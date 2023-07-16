import os
import logging

from fastapi import FastAPI
import sentry_sdk

from app.api import text_extract  # updated
sentry_sdk.init(
    dsn="https://5c74c0bf64424183a3d8fea7a803a9b0@o4505535984828416.ingest.sentry.io/4505535986335744",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,    
    profiles_sampler=profiles_sampler
)

log = logging.getLogger("uvicorn")
def create_application() -> FastAPI:
    application = FastAPI(title="API_OCR",
    version="0.1.0",
    description="OCR API project using tesseract and fastapi",
    author="Fabio"
    )
    application.include_router(text_extract.router)

    return application


app = create_application()

@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")
