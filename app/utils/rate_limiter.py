import asyncio
import time

LAST_CALL = 0
LIMIT = 1


async def rate_limit():

    global LAST_CALL

    now = time.time()

    if now - LAST_CALL < LIMIT:
        await asyncio.sleep(LIMIT)

    LAST_CALL = time.time()
