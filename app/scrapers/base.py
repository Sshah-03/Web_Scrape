"""Base scraper implementation."""

import logging
from typing import Any

import httpx
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from app.config import settings

logger = logging.getLogger(__name__)

JSONType = dict[str, Any] | list[Any]


def _should_retry(exception: BaseException) -> bool:
    """Return whether a fetch exception should trigger a retry."""
    if isinstance(exception, httpx.TimeoutException):
        return True
    if isinstance(exception, httpx.RequestError):
        return True
    if isinstance(exception, httpx.HTTPStatusError):
        return 500 <= exception.response.status_code < 600
    return False


class BaseScraper:
    """Base class for all web scrapers providing common HTTP functionality."""

    def __init__(self) -> None:
        """Initialize the scraper."""
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client, creating it if necessary."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=settings.REQUEST_TIMEOUT,
                headers={"User-Agent": settings.REDDIT_USER_AGENT},
            )
        return self._client

    async def close(self) -> None:
        """Close the shared HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @retry(
        wait=wait_exponential(min=1, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception(_should_retry),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def fetch(self, url: str) -> JSONType:
        """Fetch JSON data from a URL with retries and explicit error handling."""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            payload = response.json()
            logger.info("Fetched %s", url)
            if not isinstance(payload, (dict, list)):
                raise ValueError(f"Expected JSON object or list from {url}")
            return payload
        except httpx.TimeoutException as exc:
            logger.error("Timeout fetching %s: %s", url, exc)
            raise
        except httpx.HTTPStatusError as exc:
            logger.error("HTTP error %s while fetching %s", exc.response.status_code, url)
            raise
        except httpx.RequestError as exc:
            logger.error("Network error fetching %s: %s", url, exc)
            raise
        except ValueError as exc:
            logger.error("Invalid JSON from %s: %s", url, exc)
            raise
