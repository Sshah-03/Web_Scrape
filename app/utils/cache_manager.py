"""Caching utilities."""

import asyncio
import json
import logging
from pathlib import Path
from threading import RLock
from typing import Any, Optional
from urllib.parse import urlparse

import redis

from app.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Manage cache operations using Redis with a file-cache fallback."""

    def __init__(self) -> None:
        """Initialize the cache manager with Redis connection and file fallback."""
        self.redis: Optional[redis.Redis] = None
        self.use_redis = False
        self._file_lock = RLock()
        self._cache_file = Path(settings.FILE_CACHE)
        self._setup_redis()

    def _setup_redis(self) -> None:
        """Set up Redis connection and validate it."""
        try:
            parsed = urlparse(settings.REDIS_URL)
            self.redis = redis.Redis(
                host=parsed.hostname,
                port=parsed.port,
                password=parsed.password,
                db=int((parsed.path or "/0").strip("/") or 0),
                decode_responses=True,
            )
            self.redis.ping()
            self.use_redis = True
            logger.info("Redis cache enabled at %s", settings.REDIS_URL)
        except Exception as exc:
            logger.warning(
                "Redis unavailable at %s, falling back to file cache: %s",
                settings.REDIS_URL,
                exc,
            )
            self.use_redis = False

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from cache."""
        if self.use_redis and self.redis:
            try:
                data = await asyncio.to_thread(self.redis.get, key)
                if data is not None:
                    logger.debug("Redis cache hit for key: %s", key)
                    return json.loads(data)
                logger.debug("Redis cache miss for key: %s", key)
                return None
            except Exception as exc:
                logger.error("Redis get error for key %s: %s", key, exc)

        return await asyncio.to_thread(self._get_from_file, key)

    async def set(self, key: str, value: Any) -> None:
        """Store a value in cache."""

        def _json_default(obj: Any) -> Any:
            """Serialize types not supported by json.dumps."""
            try:
                from pydantic import BaseModel
            except ImportError:
                BaseModel = None  # type: ignore[assignment]

            if BaseModel and isinstance(obj, BaseModel):
                return obj.model_dump(mode="json")
            if hasattr(obj, "isoformat"):
                return obj.isoformat()
            if isinstance(obj, set):
                return list(obj)
            raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

        serialized = json.dumps(value, default=_json_default)
        json_safe_value = json.loads(serialized)

        if self.use_redis and self.redis:
            try:
                await asyncio.to_thread(self.redis.setex, key, settings.CACHE_TTL, serialized)
                logger.debug("Cached in Redis: %s", key)
                return
            except Exception as exc:
                logger.error("Redis set error for key %s: %s", key, exc)

        await asyncio.to_thread(self._set_in_file, key, json_safe_value)

    def _load_file_cache(self) -> dict[str, Any]:
        """Load the file-backed cache into memory."""
        if not self._cache_file.exists():
            return {}

        try:
            return json.loads(self._cache_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            logger.warning("File cache is corrupted, resetting it: %s", exc)
            return {}

    def _get_from_file(self, key: str) -> Optional[Any]:
        """Read a cached value from the file store."""
        with self._file_lock:
            cache = self._load_file_cache()
        value = cache.get(key)
        logger.debug("File cache %s for key: %s", "hit" if value is not None else "miss", key)
        return value

    def _set_in_file(self, key: str, value: Any) -> None:
        """Persist a cached value in the file store."""
        try:
            with self._file_lock:
                cache = self._load_file_cache()
                cache[key] = value
                self._cache_file.write_text(json.dumps(cache, indent=2), encoding="utf-8")
            logger.debug("Cached in file: %s", key)
        except Exception as exc:
            logger.error("File cache write error for key %s: %s", key, exc)


cache_manager = CacheManager()
