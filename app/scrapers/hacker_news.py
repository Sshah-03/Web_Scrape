
from typing import List
from pydantic import ValidationError
import logging
from app.scrapers.base import BaseScraper
from app.models.schemas import HackerNewsItem
from app.config import settings
from app.utils.decorators import cached, rate_limit

logger=logging.getLogger(__name__)

class HackerNewsScraper(BaseScraper):

    @cached("hn")
    @rate_limit
    async def scrape(self)->List[dict]:
        ids=await self.fetch(settings.HACKERNEWS_URL)
        results=[]
        for i in ids[:10]:
            data=await self.fetch(settings.HACKERNEWS_ITEM_URL.format(id=i))
            try:
                item=HackerNewsItem(
                    title=data.get("title",""),
                    url=data.get("url"),
                    score=data.get("score",0)
                )
                results.append(item.model_dump())
            except ValidationError as e:
                logger.error("Validation error %s",e)
        return results
