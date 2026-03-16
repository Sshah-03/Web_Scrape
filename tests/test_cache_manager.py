"""Tests for cache manager behavior."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.config import settings
from app.utils.cache_manager import CacheManager


@pytest.mark.asyncio()
async def test_cache_manager_uses_redis_when_available() -> None:
    """Redis should be used when the connection is healthy."""
    with patch("redis.Redis") as mock_redis_class:
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_redis.get.return_value = '{"cached": true}'
        mock_redis_class.return_value = mock_redis

        cache = CacheManager()
        await cache.set("key", {"cached": True})
        result = await cache.get("key")

    mock_redis.setex.assert_called_once_with("key", settings.CACHE_TTL, '{"cached": true}')
    mock_redis.get.assert_called_once_with("key")
    assert result == {"cached": True}


@pytest.mark.asyncio()
async def test_cache_manager_falls_back_to_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """File cache should be used when Redis is unavailable."""
    cache_file = tmp_path / "cache.json"
    monkeypatch.setattr("app.config.settings.FILE_CACHE", str(cache_file))

    with patch("redis.Redis", side_effect=RuntimeError("redis unavailable")):
        cache = CacheManager()
        await cache.set("file-key", {"value": 1})
        result = await cache.get("file-key")

    assert result == {"value": 1}
    assert json.loads(cache_file.read_text(encoding="utf-8"))["file-key"] == {"value": 1}


@pytest.mark.asyncio()
async def test_cache_manager_handles_corrupt_file_cache(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Corrupt cache files should not crash lookups."""
    cache_file = tmp_path / "cache.json"
    cache_file.write_text("{not-json", encoding="utf-8")
    monkeypatch.setattr("app.config.settings.FILE_CACHE", str(cache_file))

    with patch("redis.Redis", side_effect=RuntimeError("redis unavailable")):
        cache = CacheManager()
        result = await cache.get("missing")

    assert result is None
