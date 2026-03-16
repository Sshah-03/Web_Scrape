import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.config import settings
from app.logging_config import setup_logging

setup_logging()

app = FastAPI(title=settings.APP_NAME, description=settings.API_DESCRIPTION)

# Provide a backward-compatible name for uvicorn invocation
main = app

app.include_router(router)

# Serve the frontend directory (index.html at root)
static_dir = Path(os.path.join(os.path.dirname(__file__), "..", "frontend")).resolve()
app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
