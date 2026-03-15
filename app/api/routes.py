import asyncio
import logging
from typing import List, Union
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.scrapers.hacker_news import HackerNewsScraper
from app.scrapers.reddit import RedditScraper
from app.scrapers.fakestore import FakeStoreScraper
from app.services.export_service import export_to_csv
from app.models.schemas import HackerNewsItem, RedditItem, FakeStoreItem, ScrapeResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize scrapers
hn = HackerNewsScraper()
rd = RedditScraper()
fs = FakeStoreScraper()


@router.get("/scrape")
async def scrape_all() -> ScrapeResponse:
    """Scrape data from all sources concurrently.

    Returns:
        ScrapeResponse containing scraped data from all sources.
    """
    print("Starting scrape_all")
    try:
        logger.info("Starting concurrent scrape of all sources")
        # Run all scrapers concurrently
        tasks = [hn.scrape(), rd.scrape(), fs.scrape()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle any exceptions
        all_data = []
        for i, result in enumerate(results):
            source_names = ["HackerNews", "Reddit", "FakeStore"]
            if isinstance(result, Exception):
                logger.error("Failed to scrape %s: %s", source_names[i], result)
                print(f"Failed to scrape {source_names[i]}: {result}")
                continue
            all_data.extend(result)

        logger.info("Successfully scraped %d items from all sources", len(all_data))
        print(f"Successfully scraped {len(all_data)} items")
        return ScrapeResponse(data=all_data)

    except Exception as e:
        logger.error("Error during scraping: %s", e)
        print(f"Error during scraping: {e}")
        raise HTTPException(status_code=500, detail="Scraping failed")


@router.get("/export")
async def export_csv() -> FileResponse:
    """Export scraped data to CSV file.

    Returns:
        FileResponse with the CSV file.
    """
    try:
        logger.info("Starting CSV export")
        # Get data from scrape endpoint
        scrape_response = await scrape_all()
        data = [item.model_dump() for item in scrape_response.data]

        # Use export service
        file_path = export_to_csv(data)

        logger.info("CSV export completed: %s", file_path)
        return FileResponse(
            path=file_path,
            filename="scraped_data.csv",
            media_type="text/csv",
        )
    except Exception as e:
        logger.error("Error during CSV export: %s", e)
        raise HTTPException(status_code=500, detail="Export failed")