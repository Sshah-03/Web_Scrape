"""Hacker News scraper."""

import logging

from pydantic import ValidationError

from app.config import settings
from app.models.schemas import HackerNewsItem, HackerNewsItemResponse, HackerNewsTopStoriesResponse
from app.scrapers.base import BaseScraper
from app.utils.decorators import cached, rate_limit

logger = logging.getLogger(__name__)


class HackerNewsScraper(BaseScraper):
    """Scraper for Hacker News top stories."""

    @cached("hn")
    @rate_limit
    async def scrape(self) -> list[HackerNewsItem]:
        """Scrape top stories from Hacker News."""
        raw_ids = await self.fetch(settings.HACKERNEWS_URL)
        ids = HackerNewsTopStoriesResponse.model_validate(raw_ids).root

        results: list[HackerNewsItem] = []
        for item_id in ids[: settings.SCRAPE_LIMIT]:
            try:
                raw_data = await self.fetch(settings.HACKERNEWS_ITEM_URL.format(id=item_id))
                item = HackerNewsItem.model_validate(
                    HackerNewsItemResponse.model_validate(raw_data).model_dump(mode="json")
                )
                results.append(item)
            except ValidationError as exc:
                logger.error("Validation error for Hacker News item %s: %s", item_id, exc)
            except Exception as exc:
                logger.error("Error fetching Hacker News item %s: %s", item_id, exc)

        logger.info("Scraped %d Hacker News items", len(results))
        return results
