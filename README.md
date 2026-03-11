Async Web Scraper (FastAPI)
Overview

The Async Web Scraper is a Python-based web application that collects data from multiple online sources concurrently using asynchronous programming. The project is built using FastAPI, enabling high-performance API endpoints and a lightweight web interface to trigger scraping tasks.

The application scrapes data from multiple sources such as:

FakeStore API (Products)

Hacker News (Top stories)

Reddit (Top posts)

The scraped data is displayed through a clean web interface where users can:

Scrape all websites at once

Scrape one website at a time

View images, titles, prices, and links

Download the scraped results as a CSV file

This project demonstrates concepts like asynchronous programming, modular architecture, API integration, and data processing.

Features
Asynchronous Web Scraping

Uses Python async/await and httpx to scrape multiple sources concurrently for improved performance.

Multiple Data Sources

The scraper collects information from:

FakeStore API (product listings)

Hacker News (front page stories)

Reddit (top posts)

Selective Scraping

Users can select which website to scrape using a dropdown menu:

All websites

FakeStore

HackerNews

Reddit

Image and Link Support

Product images and article links are displayed directly in the UI.

CSV Export

Users can download the scraped results in CSV format for further analysis.

Clean User Interface

The application provides a simple dashboard where results are displayed in scrollable card layouts.

Caching

A caching mechanism is implemented to avoid unnecessary repeated requests.

Rate Limiting

Rate limiting prevents excessive API requests and simulates production-grade scraping behavior.

Technologies Used
Technology	Purpose
Python	Core programming language
FastAPI	Web framework for API development
httpx	Asynchronous HTTP requests
asyncio	Concurrent scraping execution
Jinja2	Server-side HTML templating
Pandas	Data processing and CSV export
HTML/CSS	Frontend interface

WORKFLOW

<img width="644" height="1251" alt="Web_Scrap_Workflow drawio" src="https://github.com/user-attachments/assets/5c940c5a-0731-47bc-8aa3-1794117ac53e" />
