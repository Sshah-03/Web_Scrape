"""Application configuration."""

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """Central application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "Web Scraper"
    API_DESCRIPTION: str = "Async web scraper with FastAPI"
    LOG_LEVEL: str = "INFO"

    HACKERNEWS_URL: str = "https://hacker-news.firebaseio.com/v0/topstories.json"
    HACKERNEWS_ITEM_URL: str = "https://hacker-news.firebaseio.com/v0/item/{id}.json"
    REDDIT_URL: str = "https://www.reddit.com/r/python/top.json"
    REDDIT_BASE_URL: str = "https://reddit.com"
    REDDIT_USER_AGENT: str = "web-scraper/1.0"
    FAKESTORE_URL: str = "https://fakestoreapi.com/products"

    REQUEST_TIMEOUT: float = 10.0
    RATE_LIMIT: int = 5
    SCRAPE_LIMIT: int = 10

    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 300
    CACHE_NAMESPACE: str = "web_scraper"

    OUTPUT_FILE: str = "scraped_data.csv"
    FILE_CACHE: str = "cache.json"


settings = Settings()
