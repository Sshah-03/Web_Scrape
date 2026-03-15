
from typing import List
from pydantic import ValidationError
import logging
from app.scrapers.base import BaseScraper
from app.models.schemas import RedditItem
from app.config import settings
from app.utils.decorators import cached, rate_limit

logger = logging.getLogger(__name__)


class RedditScraper(BaseScraper):
    """Scraper for Reddit top posts."""

    @cached("reddit")
    @rate_limit
    async def scrape(self) -> List[RedditItem]:
        """Scrape top posts from Reddit.

        Returns:
            List of RedditItem objects.
        """
        data = await self.fetch(settings.REDDIT_URL)
        results = []
        for post in data.get("data", {}).get("children", []):
            d = post.get("data", {})
            try:
                item = RedditItem(
                    title=d.get("title", ""),
                    score=d.get("score", 0),
                    url=f"https://reddit.com{d.get('permalink', '')}"
                )
                results.append(item)
            except ValidationError as e:
                logger.error("Validation error for Reddit post: %s", e)
            except Exception as e:
                logger.error("Error processing Reddit post: %s", e)
        logger.info("Scraped %d Reddit items", len(results))
        return results
