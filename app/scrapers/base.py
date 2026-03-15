
import httpx
import logging
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type, before_sleep_log
from app.config import settings

logger = logging.getLogger(__name__)


class BaseScraper:
    """Base class for all web scrapers providing common HTTP functionality."""

    def __init__(self):
        """Initialize the scraper."""
        self._client = None

    @property
    def client(self):
        """Get the HTTP client, creating it if necessary."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT)
        return self._client

    async def close(self):
        """Close the shared HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @retry(
        wait=wait_exponential(min=1, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def fetch(self, url: str) -> dict:
        """Fetch JSON data from a URL with retry logic.

        Args:
            url: The URL to fetch data from.

        Returns:
            The JSON response data.

        Raises:
            httpx.TimeoutException: If the request times out.
            httpx.HTTPStatusError: If the response has an error status.
            httpx.RequestError: If there's a network or other request error.
        """
        try:
            r = await self.client.get(url)
            r.raise_for_status()
            logger.info("Fetched %s", url)
            return r.json()
        except httpx.TimeoutException as e:
            logger.error("Timeout fetching %s", url)
            raise e
        except httpx.HTTPStatusError as e:
            # Only retry on 5xx errors
            if 500 <= e.response.status_code < 600:
                logger.warning("Server error %d for %s, will retry", e.response.status_code, url)
                raise e
            else:
                logger.error("Client error %d for %s", e.response.status_code, url)
                raise e
        except httpx.RequestError as e:
            logger.error("Request error fetching %s", url)
            raise e
