
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Union


class HackerNewsItem(BaseModel):
    """Represents a Hacker News story item."""
    title: str
    url: Optional[HttpUrl] = None
    score: int


class RedditItem(BaseModel):
    """Represents a Reddit post item."""
    title: str
    score: int
    url: HttpUrl


class FakeStoreItem(BaseModel):
    """Represents a FakeStore product item."""
    title: str
    price: float
    category: str


class ScrapeResponse(BaseModel):
    """Response model for scrape endpoints."""
    data: List[Union[HackerNewsItem, RedditItem, FakeStoreItem]]


class ExportResponse(BaseModel):
    """Response model for export endpoints."""
    message: str
    file_path: str
