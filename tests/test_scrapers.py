import pytest
from unittest.mock import AsyncMock, patch
from app.scrapers.hacker_news import HackerNewsScraper
from app.scrapers.reddit import RedditScraper
from app.scrapers.fakestore import FakeStoreScraper
from app.models.schemas import HackerNewsItem, RedditItem, FakeStoreItem


class TestScrapers:
    """Test cases for web scrapers."""

    @pytest.mark.asyncio
    async def test_hacker_news_scraper(self):
        """Test Hacker News scraper."""
        scraper = HackerNewsScraper()

        # Mock the fetch method
        mock_data = [1, 2, 3]
        item_data = {"title": "Test Story", "url": "https://example.com", "score": 100}

        with patch.object(scraper, 'fetch', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = [mock_data, item_data, item_data, item_data]

            results = await scraper.scrape()

            assert len(results) == 3
            assert all(isinstance(item, HackerNewsItem) for item in results)
            assert results[0].title == "Test Story"

    @pytest.mark.asyncio
    async def test_reddit_scraper(self):
        """Test Reddit scraper."""
        scraper = RedditScraper()

        mock_data = {
            "data": {
                "children": [
                    {"data": {"title": "Test Post", "score": 50, "permalink": "/r/test/123"}}
                ]
            }
        }

        with patch.object(scraper, 'fetch', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_data

            results = await scraper.scrape()

            assert len(results) == 1
            assert isinstance(results[0], RedditItem)
            assert results[0].title == "Test Post"
            assert results[0].url == "https://reddit.com/r/test/123"

    @pytest.mark.asyncio
    async def test_fakestore_scraper(self):
        """Test FakeStore scraper."""
        scraper = FakeStoreScraper()

        mock_data = [
            {"title": "Test Product", "price": 29.99, "category": "electronics"}
        ]

        with patch.object(scraper, 'fetch', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_data

            results = await scraper.scrape()

            assert len(results) == 1
            assert isinstance(results[0], FakeStoreItem)
            assert results[0].title == "Test Product"
            assert results[0].price == 29.99