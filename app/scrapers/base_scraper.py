import httpx

class BaseScraper:

    async def fetch(self, url):
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()
