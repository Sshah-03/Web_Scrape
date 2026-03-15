
from pydantic import BaseModel, HttpUrl
from typing import Optional

class HackerNewsItem(BaseModel):
    title: str
    url: Optional[HttpUrl] = None
    score: int

class RedditItem(BaseModel):
    title: str
    score: int
    url: HttpUrl

class FakeStoreItem(BaseModel):
    title: str
    price: float
    category: str
