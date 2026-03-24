"""API routes for scraping and export."""

import asyncio
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.config import settings
from app.models.schemas import (
    ScrapeResponse,
    SnapshotCreateRequest,
    SnapshotCreateResponse,
    SnapshotListResponse,
)
from app.scrapers.fakestore import FakeStoreScraper
from app.scrapers.hacker_news import HackerNewsScraper
from app.scrapers.reddit import RedditScraper
from app.services.export_service import export_to_csv
from app.services.snapshot_service import list_snapshots, save_snapshot

logger = logging.getLogger(__name__)

router = APIRouter()

hn = HackerNewsScraper()
rd = RedditScraper()
fs = FakeStoreScraper()


@router.get("/scrape", response_model=ScrapeResponse)
async def scrape_all() -> ScrapeResponse:
    """Scrape data from all sources concurrently."""
    try:
        logger.info("Starting concurrent scrape of all sources")
        results = await asyncio.gather(
            hn.scrape(),
            rd.scrape(),
            fs.scrape(),
            return_exceptions=True,
        )

        all_data = []
        source_names = ["HackerNews", "Reddit", "FakeStore"]
        for source_name, result in zip(source_names, results):
            if isinstance(result, Exception):
                logger.error("Failed to scrape %s: %s", source_name, result)
                continue
            all_data.extend(result)
            logger.info("Scraped %d items from %s", len(result), source_name)

        try:
            export_to_csv([item.model_dump(mode="json") for item in all_data])
        except Exception as exc:
            logger.error("CSV refresh failed after scrape: %s", exc)
        logger.info("Successfully scraped %d items from all sources", len(all_data))
        return ScrapeResponse(data=all_data)
    except Exception as exc:
        logger.error("Error during scraping: %s", exc)
        raise HTTPException(status_code=500, detail="Scraping failed") from exc


@router.get("/export")
async def export_csv() -> FileResponse:
    """Export scraped data to a CSV file."""
    try:
        logger.info("Starting CSV export")
        scrape_response = await scrape_all()
        data = [item.model_dump(mode="json") for item in scrape_response.data]
        file_path = export_to_csv(data)
        logger.info("CSV export completed: %s", file_path)
        return FileResponse(
            path=file_path,
            filename=Path(settings.OUTPUT_FILE).name,
            media_type="text/csv",
        )
    except Exception as exc:
        logger.error("Error during CSV export: %s", exc)
        raise HTTPException(status_code=500, detail="Export failed") from exc


@router.post("/snapshots", response_model=SnapshotCreateResponse)
async def create_snapshot(payload: SnapshotCreateRequest) -> SnapshotCreateResponse:
    """Store the currently displayed scraped data as a snapshot."""
    try:
        if not payload.data:
            raise HTTPException(status_code=400, detail="Snapshot data cannot be empty")

        snapshot = save_snapshot([item.model_dump(mode="json") for item in payload.data])
        return SnapshotCreateResponse(message="Snapshot stored successfully", **snapshot)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error while saving snapshot: %s", exc)
        raise HTTPException(status_code=500, detail="Snapshot save failed") from exc


@router.get("/snapshots", response_model=SnapshotListResponse)
async def get_snapshots(limit: int = Query(default=20, ge=1, le=100)) -> SnapshotListResponse:
    """List the most recent saved snapshots."""
    try:
        return SnapshotListResponse(snapshots=list_snapshots(limit=limit))
    except Exception as exc:
        logger.error("Error while listing snapshots: %s", exc)
        raise HTTPException(status_code=500, detail="Snapshot list failed") from exc
