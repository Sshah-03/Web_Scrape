import asyncio
from app.scrapers.fakestore_scraper import FakeStoreScraper
from app.scrapers.hackernews_scraper import HackerNewsScraper
from app.scrapers.reddit_scraper import RedditScraper


async def run_scrapers(source):

    fakestore = FakeStoreScraper()
    hackernews = HackerNewsScraper()
    reddit = RedditScraper()

    if source == "fakestore":
        return await fakestore.scrape()

    if source == "hackernews":
        return await hackernews.scrape()

    if source == "reddit":
        return await reddit.scrape()

    results = await asyncio.gather(
        fakestore.scrape(),
        hackernews.scrape(),
        reddit.scrape()
    )

    combined = [item for sublist in results for item in sublist]

    return combined
