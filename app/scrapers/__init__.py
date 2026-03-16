"""Scrapers Package."""

from .base import BaseScraper
from .fakestore import FakeStoreScraper
from .hacker_news import HackerNewsScraper
from .reddit import RedditScraper

__all__ = ["BaseScraper", "FakeStoreScraper", "HackerNewsScraper", "RedditScraper"]
