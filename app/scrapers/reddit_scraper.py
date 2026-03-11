from app.scrapers.base_scraper import BaseScraper

class RedditScraper(BaseScraper):

    async def scrape(self):
        url = "https://www.reddit.com/r/python/top.json?limit=10"
        data = await self.fetch(url)

        posts = []

        for post in data["data"]["children"]:
            posts.append({
                "source": "Reddit",
                "title": post["data"]["title"],
                "score": post["data"]["score"]
            })

        return posts
