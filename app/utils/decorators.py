"""Decorator helpers for scrapers."""

import functools
import logging
from typing import Any, Awaitable, Callable, TypeVar

from app.utils.cache_manager import cache_manager
from app.utils.rate_limiter import rate_limiter

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Awaitable[Any]])


def _build_cache_key(
    key_prefix: str, func: F, args: tuple[Any, ...], kwargs: dict[str, Any]
) -> str:
    """Build a stable cache key for a wrapped async function."""
    serializable_args = args[1:] if args and hasattr(args[0], func.__name__) else args
    kwargs_items = tuple(sorted(kwargs.items()))
    return f"{key_prefix}:{func.__name__}:{serializable_args!r}:{kwargs_items!r}"


def cached(key_prefix: str) -> Callable[[F], F]:
    """Decorator to cache async function results."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = _build_cache_key(key_prefix, func, args, kwargs)
            cached_value = await cache_manager.get(key)
            if cached_value is not None:
                logger.debug("Cache hit %s", key)
                return cached_value
            result = await func(*args, **kwargs)
            await cache_manager.set(key, result)
            logger.debug("Cache set %s", key)
            return result

        return wrapper  # type: ignore[return-value]

    return decorator


def rate_limit(func: F) -> F:
    """Decorator to apply rate limiting to async functions."""

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        await rate_limiter.wait()
        return await func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]
