import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from app.utils.decorators import cached, rate_limit


class TestDecorators:
    """Test cases for caching and rate limiting decorators."""

    @pytest.mark.asyncio
    async def test_cached_decorator_hit(self):
        """Test cached decorator with cache hit."""
        mock_cache = AsyncMock()
        mock_cache.get.return_value = "cached_result"

        with patch('app.utils.decorators.cache_manager', mock_cache):
            @cached("test")
            async def test_func():
                return "new_result"

            result = await test_func()
            assert result == "cached_result"
            mock_cache.get.assert_called_once()
            mock_cache.set.assert_not_called()

    @pytest.mark.asyncio
    async def test_cached_decorator_miss(self):
        """Test cached decorator with cache miss."""
        mock_cache = AsyncMock()
        mock_cache.get.return_value = None

        with patch('app.utils.decorators.cache_manager', mock_cache):
            @cached("test")
            async def test_func():
                return "new_result"

            result = await test_func()
            assert result == "new_result"
            mock_cache.get.assert_called_once()
            mock_cache.set.assert_called_once_with("test:test_func", "new_result")

    @pytest.mark.asyncio
    async def test_rate_limit_decorator(self):
        """Test rate limit decorator."""
        mock_limiter = AsyncMock()

        with patch('app.utils.decorators.rate_limiter', mock_limiter):
            @rate_limit
            async def test_func():
                return "result"

            result = await test_func()
            assert result == "result"
            mock_limiter.wait.assert_called_once()