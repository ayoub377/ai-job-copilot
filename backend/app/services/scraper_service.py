# app/services/scraper_service.py
from typing import List, Dict, Any

from firecrawl import FirecrawlApp
from firecrawl.firecrawl import BatchScrapeStatusResponse, FirecrawlDocument

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


def batch_scrape_job_urls(urls: List[str]) -> List[Dict[str, Any]]:
    """
    Scrapes a list of job URLs in a single batch operation using Firecrawl.
    """
    if not FIRECRAWL_API_KEY:
        raise ValueError("Firecrawl API key is not set.")

    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

    try:
        print(f"Starting batch scrape for {len(urls)} URLs.")
        batch_response = app.batch_scrape_urls(
            urls=urls,
            formats=['markdown'],
        )
        print("Batch scrape completed.")

        results_list = []
        if isinstance(batch_response, list):
            results_list = batch_response
        elif hasattr(batch_response, 'data'):
            results_list = batch_response.data
        else:
            print(f"Firecrawl returned an unexpected data type: {type(batch_response)}")

        processed_results = []
        if not results_list:
            print("No results to process.")
            return []

        for item in results_list:
            data_dict = None
            # --- FIX: Handle FirecrawlDocument object format ---
            # The FirecrawlDocument object does not have a '.success' attribute.
            # We determine success by checking if markdown content exists.
            if isinstance(item, FirecrawlDocument):
                is_successful = item.markdown is not None
                data_dict = {
                    'success': is_successful,
                    'markdown': item.markdown,
                    'metadata': item.metadata,
                    'url': item.url
                }
            # Keep the previous checks for other potential formats.
            elif isinstance(item, tuple) and item:
                data_dict = item[0]
            elif isinstance(item, dict):
                data_dict = item
            else:
                print(f"Skipping item with unexpected format: {type(item)}")
                continue

            # Ensure we have a dictionary to work with
            if not isinstance(data_dict, dict):
                print(f"Skipping item after initial processing; not a dict: {type(data_dict)}")
                continue

            # Now, process the unified data_dict
            if data_dict.get('success') is True and data_dict.get('markdown'):
                processed_results.append(data_dict)
            elif data_dict.get('success') is False:
                error_url = data_dict.get('url', 'URL not provided in error')
                print(f"Firecrawl returned a failure for URL: {error_url}")
            else:
                print(f"Skipping item with unknown structure or no markdown: {data_dict}")

        print(f"Successfully processed {len(processed_results)} out of {len(results_list)} scrape results.")
        return processed_results

    except Exception as e:
        print(f"An unexpected error occurred during batch scraping: {e}")
        return []
