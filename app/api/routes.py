from fastapi import APIRouter
from fastapi.responses import FileResponse
import pandas as pd

from app.scrapers.hacker_news import HackerNewsScraper
from app.scrapers.reddit import RedditScraper
from app.scrapers.fakestore import FakeStoreScraper

router = APIRouter()

hn = HackerNewsScraper()
rd = RedditScraper()
fs = FakeStoreScraper()


@router.get("/scrape")
async def scrape_all():
    data = []
    data += await hn.scrape()
    data += await rd.scrape()
    data += await fs.scrape()
    return data


@router.get("/export")
async def export_csv():
    data = await scrape_all()

    df = pd.DataFrame(data)
    file_path = "scraped_data.csv"
    df.to_csv(file_path, index=False)

    return FileResponse(
        path=file_path,
        filename="scraped_data.csv",
        media_type="text/csv",
    )