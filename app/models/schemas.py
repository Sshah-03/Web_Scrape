"""Pydantic schema definitions for API and scraper payloads."""

from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, HttpUrl, RootModel


class HackerNewsItem(BaseModel):
    """Normalized Hacker News story returned by the API."""

    title: str
    url: Optional[HttpUrl] = None
    score: int


class RedditItem(BaseModel):
    """Normalized Reddit post returned by the API."""

    title: str
    score: int
    url: HttpUrl


class FakeStoreItem(BaseModel):
    """Normalized FakeStore product returned by the API."""

    title: str
    price: float
    category: str


class ScrapeResponse(BaseModel):
    """Response model for aggregate scraping endpoints."""

    data: list[Union[HackerNewsItem, RedditItem, FakeStoreItem]]


class ExportResponse(BaseModel):
    """Response metadata for export endpoints."""

    message: str
    file_path: str


class HackerNewsTopStoriesResponse(RootModel[list[int]]):
    """Validated Hacker News top-story identifier payload."""


class HackerNewsItemResponse(BaseModel):
    """Validated Hacker News item payload."""

    model_config = ConfigDict(extra="ignore")

    title: str
    url: Optional[HttpUrl] = None
    score: int


class RedditPostData(BaseModel):
    """Validated Reddit post payload."""

    model_config = ConfigDict(extra="ignore")

    title: str
    score: int
    permalink: str


class RedditPost(BaseModel):
    """Validated Reddit listing child wrapper."""

    model_config = ConfigDict(extra="ignore")

    data: RedditPostData


class RedditListingData(BaseModel):
    """Validated Reddit listing payload."""

    model_config = ConfigDict(extra="ignore")

    children: list[RedditPost]


class RedditTopResponse(BaseModel):
    """Validated Reddit top-post API response."""

    model_config = ConfigDict(extra="ignore")

    data: RedditListingData


class FakeStoreProductResponse(BaseModel):
    """Validated FakeStore product payload."""

    model_config = ConfigDict(extra="ignore")

    title: str
    price: float
    category: str


class FakeStoreProductsResponse(RootModel[list[FakeStoreProductResponse]]):
    """Validated FakeStore product collection."""
