"""Tests for caching and rate limiting decorators."""

from unittest.mock import AsyncMock, patch

import pytest

from app.utils.decorators import cached, rate_limit


@pytest.mark.asyncio()
async def test_cached_decorator_returns_cached_value() -> None:
    """Cached decorator should return a cached value on hit."""
    mock_cache = AsyncMock()
    mock_cache.get.return_value = "cached"

    with patch("app.utils.decorators.cache_manager", mock_cache):

        @cached("demo")
        async def test_func() -> str:
            return "fresh"

        result = await test_func()

    assert result == "cached"
    mock_cache.set.assert_not_called()


@pytest.mark.asyncio()
async def test_cached_decorator_stores_miss_with_argument_sensitive_key() -> None:
    """Cache keys should include call arguments."""
    mock_cache = AsyncMock()
    mock_cache.get.return_value = None

    with patch("app.utils.decorators.cache_manager", mock_cache):

        @cached("demo")
        async def test_func(value: str) -> str:
            return value.upper()

        result = await test_func("abc")

    assert result == "ABC"
    cache_key = mock_cache.set.call_args.args[0]
    assert cache_key.startswith("demo:test_func:")
    assert "abc" in cache_key


@pytest.mark.asyncio()
async def test_rate_limit_decorator_waits_before_execution() -> None:
    """Rate limit decorator should defer to the shared limiter."""
    mock_limiter = AsyncMock()

    with patch("app.utils.decorators.rate_limiter", mock_limiter):

        @rate_limit
        async def test_func() -> str:
            return "done"

        result = await test_func()

    assert result == "done"
    mock_limiter.wait.assert_awaited_once()
