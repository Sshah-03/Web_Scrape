
import functools
import logging
from typing import Any, Callable, Awaitable, TypeVar
from app.utils.cache_manager import cache_manager
from app.utils.rate_limiter import rate_limiter

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Awaitable[Any]])


def cached(key_prefix: str) -> Callable[[F], F]:
    """Decorator to cache async function results.

    Args:
        key_prefix: Prefix for cache keys.

    Returns:
        Decorated function that caches results.
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            key = f"{key_prefix}:{func.__name__}"
            cached_value = await cache_manager.get(key)
            if cached_value is not None:
                logger.debug("Cache hit %s", key)
                return cached_value
            result = await func(*args, **kwargs)
            await cache_manager.set(key, result)
            logger.debug("Cache set %s", key)
            return result
        return wrapper  # type: ignore
    return decorator


def rate_limit(func: F) -> F:
    """Decorator to apply rate limiting to async functions.

    Args:
        func: The async function to rate limit.

    Returns:
        The rate-limited function.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        await rate_limiter.wait()
        return await func(*args, **kwargs)
    return wrapper
