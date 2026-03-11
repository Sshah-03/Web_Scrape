from app.scrapers.base_scraper import BaseScraper

class HackerNewsScraper(BaseScraper):

    async def scrape(self):

        url = "https://hn.algolia.com/api/v1/search?tags=front_page"

        data = await self.fetch(url)

        results = []

        for item in data["hits"]:

            results.append({
                "source": "HackerNews",
                "title": item.get("title"),
                "url": item.get("url"),
                "points": item.get("points")
            })

        return results
