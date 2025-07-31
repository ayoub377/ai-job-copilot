# app/services/scraper_service.py

from firecrawl import FirecrawlApp
from app.core.config import FIRECRAWL_API_KEY


def scrape_job_url(url: str):
    """
    Scrapes a given URL using Firecrawl and returns the markdown content.
    """
    if not FIRECRAWL_API_KEY:
        raise ValueError("Firecrawl API key is not set.")

    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

    try:
        scraped_data = app.scrape_url(url)
        # We are interested in the markdown content for cleaner text
        return scraped_data.markdown
    except Exception as e:
        print(f"An error occurred while scraping: {e}")
        return None