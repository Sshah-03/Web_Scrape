
import asyncio
import time
import logging
from typing import NoReturn
from app.config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter using token bucket algorithm with async lock."""

    def __init__(self, rate: int) -> None:
        """Initialize the rate limiter.

        Args:
            rate: Maximum number of requests per second.
        """
        self.rate = rate
        self.lock = asyncio.Lock()
        self.last_call = 0.0

    async def wait(self) -> None:
        """Wait if necessary to maintain the rate limit."""
        async with self.lock:
            now = time.time()
            interval = 1 / self.rate
            diff = now - self.last_call
            if diff < interval:
                await asyncio.sleep(interval - diff)
            self.last_call = time.time()
            logger.debug("Rate limiter applied")


rate_limiter = RateLimiter(settings.RATE_LIMIT)
