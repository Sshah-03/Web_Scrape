"""FakeStore scraper."""

import logging

from pydantic import ValidationError

from app.config import settings
from app.models.schemas import FakeStoreItem, FakeStoreProductsResponse
from app.scrapers.base import BaseScraper
from app.utils.decorators import cached, rate_limit

logger = logging.getLogger(__name__)


class FakeStoreScraper(BaseScraper):
    """Scraper for FakeStore API products."""

    @cached("fakestore")
    @rate_limit
    async def scrape(self) -> list[FakeStoreItem]:
        """Scrape products from FakeStore."""
        raw_data = await self.fetch(settings.FAKESTORE_URL)
        products = FakeStoreProductsResponse.model_validate(raw_data).root

        results: list[FakeStoreItem] = []
        for product in products:
            try:
                item = FakeStoreItem.model_validate(product.model_dump(mode="json"))
                results.append(item)
            except ValidationError as exc:
                logger.error("Validation error for FakeStore item: %s", exc)
            except Exception as exc:
                logger.error("Error processing FakeStore item: %s", exc)

        logger.info("Scraped %d FakeStore items", len(results))
        return results
