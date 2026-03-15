
from typing import List
from pydantic import ValidationError
import logging
from app.scrapers.base import BaseScraper
from app.models.schemas import FakeStoreItem
from app.config import settings
from app.utils.decorators import cached, rate_limit

logger = logging.getLogger(__name__)


class FakeStoreScraper(BaseScraper):
    """Scraper for FakeStore API products."""

    @cached("fakestore")
    @rate_limit
    async def scrape(self) -> List[FakeStoreItem]:
        """Scrape products from FakeStore API.

        Returns:
            List of FakeStoreItem objects.
        """
        data = await self.fetch(settings.FAKESTORE_URL)
        results = []
        for p in data:
            try:
                item = FakeStoreItem(
                    title=p.get("title", ""),
                    price=float(p.get("price", 0)),
                    category=p.get("category", "")
                )
                results.append(item)
            except ValidationError as e:
                logger.error("Validation error for FakeStore item: %s", e)
            except Exception as e:
                logger.error("Error processing FakeStore item: %s", e)
        logger.info("Scraped %d FakeStore items", len(results))
        return results
