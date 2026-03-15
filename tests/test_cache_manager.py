import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
from app.utils.cache_manager import CacheManager
from app.config import settings


class TestCacheManager:
    """Test cases for CacheManager."""

    @pytest.mark.asyncio
    async def test_redis_cache_get_set(self):
        """Test Redis cache get and set operations."""
        with patch('redis.Redis') as mock_redis_class:
            mock_redis = MagicMock()
            mock_redis_class.return_value = mock_redis
            mock_redis.ping.return_value = True
            mock_redis.get.return_value = '{"test": "data"}'
            mock_redis.setex.return_value = True

            cache = CacheManager()

            # Test set
            await cache.set("test_key", {"test": "data"})
            mock_redis.setex.assert_called_once_with("test_key", settings.CACHE_TTL, '{"test": "data"}')

            # Test get
            result = await cache.get("test_key")
            assert result == {"test": "data"}
            mock_redis.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_file_cache_fallback(self):
        """Test file cache fallback when Redis is unavailable."""
        with patch('redis.Redis') as mock_redis_class:
            mock_redis_class.side_effect = Exception("Redis connection failed")

            with tempfile.TemporaryDirectory() as temp_dir:
                cache_file = os.path.join(temp_dir, "test_cache.json")

                with patch('app.config.settings.FILE_CACHE', cache_file):
                    cache = CacheManager()

                    # Test set
                    test_data = {"test": "data"}
                    await cache.set("test_key", test_data)

                    # Verify file was written
                    assert os.path.exists(cache_file)
                    with open(cache_file, 'r') as f:
                        cached = json.load(f)
                        assert cached["test_key"] == test_data

                    # Test get
                    result = await cache.get("test_key")
                    assert result == test_data

    @pytest.mark.asyncio
    async def test_cache_miss(self):
        """Test cache miss scenarios."""
        with patch('redis.Redis') as mock_redis_class:
            mock_redis = MagicMock()
            mock_redis_class.return_value = mock_redis
            mock_redis.ping.return_value = True
            mock_redis.get.return_value = None

            cache = CacheManager()

            result = await cache.get("nonexistent_key")
            assert result is None