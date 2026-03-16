"""Tests for retry and fetch behavior."""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from tenacity import wait_none

from app.scrapers.base import BaseScraper


def _response(status_code: int, payload: object | None = None) -> Mock:
    """Create a response-like mock object."""
    response = Mock()
    response.status_code = status_code
    response.json.return_value = payload
    if status_code >= 400:
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error",
            request=httpx.Request("GET", "https://example.com"),
            response=response,
        )
    return response


@pytest.mark.asyncio()
async def test_fetch_retries_request_error_then_succeeds() -> None:
    """`fetch` should retry transient network errors."""
    scraper = BaseScraper()
    scraper.fetch.retry.wait = wait_none()

    with patch.object(scraper.client, "get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = [
            httpx.RequestError("boom", request=httpx.Request("GET", "https://example.com")),
            _response(200, {"ok": True}),
        ]

        result = await scraper.fetch("https://example.com")

    assert result == {"ok": True}
    assert mock_get.await_count == 2
    await scraper.close()


@pytest.mark.asyncio()
async def test_fetch_retries_server_error_then_succeeds() -> None:
    """`fetch` should retry 5xx responses."""
    scraper = BaseScraper()
    scraper.fetch.retry.wait = wait_none()

    with patch.object(scraper.client, "get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = [_response(503), _response(200, {"ok": True})]

        result = await scraper.fetch("https://example.com")

    assert result == {"ok": True}
    assert mock_get.await_count == 2
    await scraper.close()


@pytest.mark.asyncio()
async def test_fetch_does_not_retry_client_error() -> None:
    """`fetch` should fail immediately for 4xx responses."""
    scraper = BaseScraper()
    scraper.fetch.retry.wait = wait_none()

    with patch.object(scraper.client, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = _response(404)

        with pytest.raises(httpx.HTTPStatusError):
            await scraper.fetch("https://example.com")

    assert mock_get.await_count == 1
    await scraper.close()


@pytest.mark.asyncio()
async def test_fetch_raises_for_invalid_json_shape() -> None:
    """`fetch` should reject non-dict and non-list JSON bodies."""
    scraper = BaseScraper()
    scraper.fetch.retry.wait = wait_none()

    with patch.object(scraper.client, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = _response(200, "not-json-object")

        with pytest.raises(ValueError):
            await scraper.fetch("https://example.com")

    await scraper.close()
