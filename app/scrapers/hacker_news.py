
from typing import List
from pydantic import ValidationError
import logging
from app.scrapers.base import BaseScraper
from app.models.schemas import HackerNewsItem
from app.config import settings
from app.utils.decorators import cached, rate_limit

logger = logging.getLogger(__name__)


class HackerNewsScraper(BaseScraper):
    """Scraper for Hacker News top stories."""

    @cached("hn")
    @rate_limit
    async def scrape(self) -> List[HackerNewsItem]:
        """Scrape top stories from Hacker News.

        Returns:
            List of HackerNewsItem objects.
        """
        ids = await self.fetch(settings.HACKERNEWS_URL)
        results = []
        for i in ids[:10]:
            try:
                data = await self.fetch(settings.HACKERNEWS_ITEM_URL.format(id=i))
                item = HackerNewsItem(
                    title=data.get("title", ""),
                    url=data.get("url"),
                    score=data.get("score", 0)
                )
                results.append(item)
            except ValidationError as e:
                logger.error("Validation error for HN item %s: %s", i, e)
            except Exception as e:
                logger.error("Error fetching HN item %s: %s", i, e)
        logger.info("Scraped %d Hacker News items", len(results))
        return results
