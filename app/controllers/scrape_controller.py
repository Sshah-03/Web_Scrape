from fastapi import APIRouter
from fastapi import Query
from app.services.services import run_scrapers

router = APIRouter()

@router.get("/scrape")

async def scrape(source: str = Query("all")):

    data = await run_scrapers(source)

    return {"data": data}
