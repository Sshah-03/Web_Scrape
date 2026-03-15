import json
import asyncio
import logging
from typing import Any, Optional
from urllib.parse import urlparse
import redis
from app.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching operations using Redis with file fallback."""

    def __init__(self):
        """Initialize the cache manager with Redis connection and file fallback."""
        self.redis: Optional[redis.Redis] = None
        self.use_redis = False
        self.file_lock = asyncio.Lock()
        self._setup_redis()

    def _setup_redis(self) -> None:
        """Set up Redis connection and validate it."""
        try:
            parsed = urlparse(settings.REDIS_URL)
            self.redis = redis.Redis(
                host=parsed.hostname,
                port=parsed.port,
                password=parsed.password,
                decode_responses=True
            )
            self.redis.ping()
            self.use_redis = True
            logger.info("Redis cache enabled at %s", settings.REDIS_URL)
        except Exception as e:
            logger.warning("Redis unavailable at %s, falling back to file cache: %s", settings.REDIS_URL, e)
            self.use_redis = False

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from cache.

        Args:
            key: The cache key.

        Returns:
            The cached value or None if not found.
        """
        if self.use_redis and self.redis:
            try:
                data = self.redis.get(key)
                if data:
                    logger.debug("Cache hit for key: %s", key)
                    return json.loads(data)
                logger.debug("Cache miss for key: %s", key)
                return None
            except Exception as e:
                logger.error("Redis get error for key %s: %s", key, e)
                return None

        # File fallback
        async with self.file_lock:
            try:
                with open(settings.FILE_CACHE, 'r') as f:
                    cache = json.load(f)
                value = cache.get(key)
                if value:
                    logger.debug("File cache hit for key: %s", key)
                else:
                    logger.debug("File cache miss for key: %s", key)
                return value
            except (FileNotFoundError, json.JSONDecodeError) as e:
                logger.debug("File cache read error: %s", e)
                return None

    async def set(self, key: str, value: Any) -> None:
        """Store a value in cache.

        Args:
            key: The cache key.
            value: The value to cache.
        """
        def _json_default(obj):
            """Default serializer for types not supported by json.dumps."""
            try:
                from pydantic import BaseModel
            except ImportError:
                BaseModel = None  # type: ignore

            if BaseModel and isinstance(obj, BaseModel):
                # Use json mode to ensure types like HttpUrl become plain strings
                return obj.model_dump(mode="json")
            if hasattr(obj, "isoformat"):
                return obj.isoformat()  # datetime/date
            if isinstance(obj, set):
                return list(obj)
            raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

        # Serialize to a JSON string for Redis and to ensure we cache only JSON-safe data
        serialized = json.dumps(value, default=_json_default)
        json_safe_value = json.loads(serialized)

        if self.use_redis and self.redis:
            try:
                self.redis.setex(key, settings.CACHE_TTL, serialized)
                logger.debug("Cached in Redis: %s", key)
                return
            except Exception as e:
                logger.error("Redis set error for key %s: %s", key, e)
                # Fall through to file cache

        # File fallback
        async with self.file_lock:
            try:
                cache = {}
                try:
                    with open(settings.FILE_CACHE, 'r') as f:
                        cache = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    pass

                cache[key] = json_safe_value

                with open(settings.FILE_CACHE, 'w') as f:
                    json.dump(cache, f, indent=2)
                logger.debug("Cached in file: %s", key)
            except Exception as e:
                logger.error("File cache write error: %s", e)


cache_manager = CacheManager()
