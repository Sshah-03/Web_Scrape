import pytest
import httpx
from unittest.mock import AsyncMock, patch
from tenacity import RetryError
from app.scrapers.base import BaseScraper


class TestRetryBehavior:
    """Test cases for retry behavior in scrapers."""

    @pytest.mark.asyncio
    async def test_retry_on_request_error(self):
        """Test that RequestError triggers retry."""
        scraper = BaseScraper()

        with patch.object(scraper.client, 'get', new_callable=AsyncMock) as mock_get:
            # First call raises RequestError, second succeeds
            mock_get.side_effect = [
                httpx.RequestError("Network error"),
                AsyncMock(json=AsyncMock(return_value={"data": "success"}))
            ]

            result = await scraper.fetch("https://test.com")

            assert result == {"data": "success"}
            assert mock_get.call_count == 2  # Retried once

    @pytest.mark.asyncio
    async def test_retry_on_5xx_status_error(self):
        """Test that 5xx HTTPStatusError triggers retry."""
        scraper = BaseScraper()

        with patch.object(scraper.client, 'get', new_callable=AsyncMock) as mock_get:
            # First call raises 500 error, second succeeds
            response_500 = AsyncMock()
            response_500.status_code = 500
            response_500.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Server error", request=AsyncMock(), response=response_500
            )

            response_200 = AsyncMock()
            response_200.status_code = 200
            response_200.json.return_value = {"data": "success"}

            mock_get.side_effect = [response_500, response_200]

            result = await scraper.fetch("https://test.com")

            assert result == {"data": "success"}
            assert mock_get.call_count == 2  # Retried once

    @pytest.mark.asyncio
    async def test_no_retry_on_4xx_status_error(self):
        """Test that 4xx HTTPStatusError does not trigger retry."""
        scraper = BaseScraper()

        with patch.object(scraper.client, 'get', new_callable=AsyncMock) as mock_get:
            response_404 = AsyncMock()
            response_404.status_code = 404
            response_404.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Not found", request=AsyncMock(), response=response_404
            )

            mock_get.side_effect = [response_404]

            with pytest.raises(httpx.HTTPStatusError):
                await scraper.fetch("https://test.com")

            assert mock_get.call_count == 1  # No retry