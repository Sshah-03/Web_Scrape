
import httpx, logging
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from app.config import settings

logger=logging.getLogger(__name__)

class BaseScraper:

    @retry(wait=wait_exponential(min=1,max=10),
           stop=stop_after_attempt(3),
           retry=retry_if_exception_type(httpx.RequestError))
    async def fetch(self,url:str):
        try:
            async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
                r=await client.get(url)
                r.raise_for_status()
                logger.info("Fetched %s",url)
                return r.json()
        except httpx.TimeoutException as e:
            logger.error("Timeout %s",url)
            raise e
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error %s",url)
            raise e
        except httpx.RequestError as e:
            logger.error("Request error %s",url)
            raise e
