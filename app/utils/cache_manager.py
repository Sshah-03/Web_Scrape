import time

CACHE = {}
CACHE_TTL = 60


def cache(func):

    async def wrapper(*args):

        key = func.__name__

        if key in CACHE:

            data, timestamp = CACHE[key]

            if time.time() - timestamp < CACHE_TTL:
                return data

        result = await func(*args)

        CACHE[key] = (result, time.time())

        return result

    return wrapper
