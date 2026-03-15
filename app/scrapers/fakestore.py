
from typing import List
from pydantic import ValidationError
import logging
from app.scrapers.base import BaseScraper
from app.models.schemas import FakeStoreItem
from app.config import settings
from app.utils.decorators import cached, rate_limit

logger=logging.getLogger(__name__)

class FakeStoreScraper(BaseScraper):

    @cached("fakestore")
    @rate_limit
    async def scrape(self)->List[dict]:
        data=await self.fetch(settings.FAKESTORE_URL)
        results=[]
        for p in data:
            try:
                item=FakeStoreItem(
                    title=p.get("title",""),
                    price=p.get("price",0),
                    category=p.get("category","")
                )
                results.append(item.model_dump())
            except ValidationError as e:
                logger.error("Validation error %s",e)
        return results
