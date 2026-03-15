# Async Web Scraper (FastAPI)

A production-grade asynchronous web scraper built with FastAPI that collects data from multiple online sources concurrently.

## Overview

This application scrapes data from three sources:
- **FakeStore API**: Product listings
- **Hacker News**: Top stories
- **Reddit**: Top posts in r/python

## Features

- **Asynchronous Scraping**: Uses Python async/await with httpx for concurrent requests
- **Redis Caching**: Optional Redis caching with file fallback
- **Rate Limiting**: Prevents excessive API requests
- **Retry Logic**: Automatic retries on network errors and 5xx responses
- **CSV Export**: Download scraped data as CSV
- **Web Interface**: Simple dashboard to trigger scraping and view results
- **Type Safety**: Full type hints and Pydantic validation
- **Logging**: Comprehensive logging with configurable levels
- **Testing**: Complete test suite with pytest

## Technologies Used

- **Python 3.8+**
- **FastAPI**: Web framework
- **httpx**: Async HTTP client
- **Redis**: Caching (optional)
- **Pandas**: Data processing
- **Pydantic**: Data validation
- **Tenacity**: Retry logic
- **pytest**: Testing

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and configure settings
4. Run: `uvicorn app.main:app --reload`

## Configuration

Configure via environment variables or `.env` file:

- `REDIS_URL`: Redis connection URL (defaults to localhost:6379)
- `CACHE_TTL`: Cache expiration time in seconds
- `RATE_LIMIT`: Requests per second limit
- `REQUEST_TIMEOUT`: HTTP request timeout

## API Endpoints

- `GET /`: Web interface
- `GET /scrape`: Scrape all sources concurrently
- `GET /export`: Download CSV of scraped data

## Development

- Format code: `black .`
- Lint code: `flake8 .`
- Run tests: `pytest`
