"""Reddit scraper."""

import logging

from pydantic import ValidationError

from app.config import settings
from app.models.schemas import RedditItem, RedditTopResponse
from app.scrapers.base import BaseScraper
from app.utils.decorators import cached, rate_limit

logger = logging.getLogger(__name__)


class RedditScraper(BaseScraper):
    """Scraper for Reddit top posts."""

    @cached("reddit")
    @rate_limit
    async def scrape(self) -> list[RedditItem]:
        """Scrape top posts from Reddit."""
        raw_data = await self.fetch(settings.REDDIT_URL)
        response = RedditTopResponse.model_validate(raw_data)

        results: list[RedditItem] = []
        for post in response.data.children:
            try:
                item = RedditItem(
                    title=post.data.title,
                    score=post.data.score,
                    url=f"{settings.REDDIT_BASE_URL}{post.data.permalink}",
                )
                results.append(item)
            except ValidationError as exc:
                logger.error("Validation error for Reddit post: %s", exc)
            except Exception as exc:
                logger.error("Error processing Reddit post: %s", exc)

        logger.info("Scraped %d Reddit items", len(results))
        return results
