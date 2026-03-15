from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from app.api.routes import router
from app.logging_config import setup_logging

setup_logging()

app = FastAPI(title="Web Scraper API", description="Async web scraper with FastAPI")

# Provide a backward-compatible name for uvicorn invocation
main = app

app.include_router(router)

# Serve the frontend directory (index.html at root)
static_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
