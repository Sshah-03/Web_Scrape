"""Rate limiting utilities."""

import asyncio
import logging
import time
from threading import Lock

from app.config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Thread-safe async rate limiter."""

    def __init__(self, rate: int) -> None:
        """Initialize the rate limiter."""
        self.rate = rate
        self._interval = 1 / rate
        self._lock = Lock()
        self._next_available = 0.0

    async def wait(self) -> None:
        """Wait if necessary to maintain the configured rate limit."""
        with self._lock:
            now = time.monotonic()
            scheduled = max(now, self._next_available)
            delay = max(0.0, scheduled - now)
            self._next_available = scheduled + self._interval

        if delay > 0:
            logger.debug("Rate limiter sleeping for %.3f seconds", delay)
            await asyncio.sleep(delay)


rate_limiter = RateLimiter(settings.RATE_LIMIT)
