import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response

from app.api.routes import router
from app.config import settings
from app.logging_config import setup_logging
from app.services.snapshot_service import init_snapshot_db

setup_logging()


class NoCacheStaticFiles(StaticFiles):
    """Serve frontend assets with headers that avoid stale browser caches."""

    async def get_response(self, path: str, scope: dict) -> Response:
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

app = FastAPI(title=settings.APP_NAME, description=settings.API_DESCRIPTION)

# Provide a backward-compatible name for uvicorn invocation
main = app

init_snapshot_db()

app.include_router(router)

# Serve the frontend directory (index.html at root)
static_dir = Path(os.path.join(os.path.dirname(__file__), "..", "frontend")).resolve()
app.mount("/", NoCacheStaticFiles(directory=static_dir, html=True), name="frontend")
