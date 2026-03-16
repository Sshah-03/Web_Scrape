"""Tests for scraper validation and normalization."""

from unittest.mock import AsyncMock, patch

import pytest
from pydantic import ValidationError

from app.models.schemas import FakeStoreItem, HackerNewsItem, RedditItem
from app.scrapers.fakestore import FakeStoreScraper
from app.scrapers.hacker_news import HackerNewsScraper
from app.scrapers.reddit import RedditScraper


@pytest.mark.asyncio()
async def test_hacker_news_scraper_returns_valid_items() -> None:
    """Hacker News scraper should normalize valid items."""
    scraper = HackerNewsScraper()

    with patch.object(scraper, "fetch", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = [
            [1, 2],
            {"title": "First", "url": "https://example.com/1", "score": 10},
            {"title": "Second", "url": "https://example.com/2", "score": 20},
        ]

        results = await scraper.scrape()

    assert results == [
        HackerNewsItem(title="First", url="https://example.com/1", score=10),
        HackerNewsItem(title="Second", url="https://example.com/2", score=20),
    ]


@pytest.mark.asyncio()
async def test_hacker_news_scraper_raises_on_invalid_top_story_payload() -> None:
    """Hacker News scraper should fail fast on invalid top story lists."""
    scraper = HackerNewsScraper()

    with patch.object(scraper, "fetch", new_callable=AsyncMock, return_value={"invalid": True}):
        with pytest.raises(ValidationError):
            await scraper.scrape()


@pytest.mark.asyncio()
async def test_reddit_scraper_returns_valid_items() -> None:
    """Reddit scraper should validate the response wrapper."""
    scraper = RedditScraper()

    with patch.object(scraper, "fetch", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = {
            "data": {
                "children": [
                    {"data": {"title": "Test", "score": 3, "permalink": "/r/python/comments/1"}}
                ]
            }
        }

        results = await scraper.scrape()

    assert results == [
        RedditItem(title="Test", score=3, url="https://reddit.com/r/python/comments/1")
    ]


@pytest.mark.asyncio()
async def test_reddit_scraper_raises_on_invalid_structure() -> None:
    """Reddit scraper should reject malformed API responses."""
    scraper = RedditScraper()

    with patch.object(scraper, "fetch", new_callable=AsyncMock, return_value={"unexpected": []}):
        with pytest.raises(ValidationError):
            await scraper.scrape()


@pytest.mark.asyncio()
async def test_fakestore_scraper_returns_valid_items() -> None:
    """FakeStore scraper should normalize product data."""
    scraper = FakeStoreScraper()

    with patch.object(
        scraper,
        "fetch",
        new_callable=AsyncMock,
        return_value=[{"title": "Keyboard", "price": 99.0, "category": "electronics"}],
    ):
        results = await scraper.scrape()

    assert results == [FakeStoreItem(title="Keyboard", price=99.0, category="electronics")]


@pytest.mark.asyncio()
async def test_fakestore_scraper_raises_on_invalid_structure() -> None:
    """FakeStore scraper should reject non-list payloads."""
    scraper = FakeStoreScraper()

    with patch.object(scraper, "fetch", new_callable=AsyncMock, return_value={"unexpected": []}):
        with pytest.raises(ValidationError):
            await scraper.scrape()
