
import functools, logging
from app.utils.cache_manager import cache_manager
from app.utils.rate_limiter import rate_limiter

logger = logging.getLogger(__name__)

def cached(key_prefix:str):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args,**kwargs):
            key=f"{key_prefix}:{func.__name__}"
            cached=cache_manager.get(key)
            if cached:
                logger.debug("Cache hit %s",key)
                return cached
            result=await func(*args,**kwargs)
            cache_manager.set(key,result)
            logger.debug("Cache set %s",key)
            return result
        return wrapper
    return decorator

def rate_limit(func):
    @functools.wraps(func)
    async def wrapper(*args,**kwargs):
        await rate_limiter.wait()
        return await func(*args,**kwargs)
    return wrapper
