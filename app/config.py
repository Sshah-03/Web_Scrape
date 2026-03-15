
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "Web Scraper"

    HACKERNEWS_URL: str = "https://hacker-news.firebaseio.com/v0/topstories.json"
    HACKERNEWS_ITEM_URL: str = "https://hacker-news.firebaseio.com/v0/item/{id}.json"

    REDDIT_URL: str = "https://www.reddit.com/r/python/top.json"

    FAKESTORE_URL: str = "https://fakestoreapi.com/products"

    REQUEST_TIMEOUT: int = 10
    RATE_LIMIT: int = 5

    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 300

    OUTPUT_FILE: str = "scraped_data.csv"
    FILE_CACHE: str = "cache.json"

settings = Settings()
