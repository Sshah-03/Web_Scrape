from app.scrapers.base_scraper import BaseScraper

class FakeStoreScraper(BaseScraper):

    async def scrape(self):

        url = "https://fakestoreapi.com/products"

        data = await self.fetch(url)

        results = []

        for item in data:

            results.append({
                "source": "FakeStore",
                "title": item.get("title"),
                "price": item.get("price"),
                "image": item.get("image"),
                "link": f"https://fakestoreapi.com/products/{item.get('id')}"
            })

        return results
