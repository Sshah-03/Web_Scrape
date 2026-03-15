
from typing import List
from pydantic import ValidationError
import logging
from app.scrapers.base import BaseScraper
from app.models.schemas import RedditItem
from app.config import settings
from app.utils.decorators import cached, rate_limit

logger=logging.getLogger(__name__)

class RedditScraper(BaseScraper):

    @cached("reddit")
    @rate_limit
    async def scrape(self)->List[dict]:
        data=await self.fetch(settings.REDDIT_URL)
        results=[]
        for post in data.get("data",{}).get("children",[]):
            d=post.get("data",{})
            try:
                item=RedditItem(
                    title=d.get("title",""),
                    score=d.get("score",0),
                    url="https://reddit.com"+d.get("permalink","")
                )
                results.append(item.model_dump())
            except ValidationError as e:
                logger.error("Validation error %s",e)
        return results
