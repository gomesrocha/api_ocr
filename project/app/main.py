import os
import logging

from fastapi import FastAPI
import sentry_sdk


sentry_sdk.init(
    dsn="https://5c74c0bf64424183a3d8fea7a803a9b0@o4505535984828416.ingest.sentry.io/4505535986335744",

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production,
    traces_sample_rate=1.0,
)

from api import text_extract  # updated

log = logging.getLogger("uvicorn")

def create_application() -> FastAPI:
    application = FastAPI()
    application.include_router(text_extract.router)

    return application


app = create_application()

@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")