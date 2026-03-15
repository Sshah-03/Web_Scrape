import pytest
import asyncio
from unittest.mock import AsyncMock
from app.config import Settings


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    return Settings(
        APP_NAME="Test Scraper",
        HACKERNEWS_URL="https://test-hn.com",
        HACKERNEWS_ITEM_URL="https://test-hn.com/item/{id}.json",
        REDDIT_URL="https://test-reddit.com",
        FAKESTORE_URL="https://test-fakestore.com",
        REQUEST_TIMEOUT=5,
        RATE_LIMIT=10,
        REDIS_URL="redis://localhost:6379",
        CACHE_TTL=60,
        OUTPUT_FILE="test_output.csv",
        FILE_CACHE="test_cache.json"
    )