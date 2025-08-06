# app/services/linkedin_scraper_service.py

import time
import random
from typing import List, Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlencode, quote


class LinkedInJobScraper:
    def __init__(self):
        self.base_url = "https://www.linkedin.com/jobs/search"
        self.driver = None
        
    def _setup_driver(self):
        """Setup Chrome driver with appropriate options for scraping"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        return self.driver
    
    def _close_driver(self):
        """Close the driver safely"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def _build_search_url(self, keywords: str, location: str = "", experience_level: str = "", 
                         job_type: str = "", sort_by: str = "date") -> str:
        """Build LinkedIn job search URL with parameters"""
        params = {
            'keywords': keywords,
            'location': location,
            'sortBy': sort_by
        }
        
        # Add experience level filter
        if experience_level:
            experience_map = {
                'internship': '1',
                'entry': '2', 
                'associate': '3',
                'mid': '4',
                'senior': '5',
                'director': '6',
                'executive': '7'
            }
            if experience_level.lower() in experience_map:
                params['f_E'] = experience_map[experience_level.lower()]
        
        # Add job type filter
        if job_type:
            job_type_map = {
                'full-time': 'F',
                'part-time': 'P',
                'contract': 'C',
                'temporary': 'T',
                'internship': 'I'
            }
            if job_type.lower() in job_type_map:
                params['f_JT'] = job_type_map[job_type.lower()]
        
        # Remove empty parameters
        params = {k: v for k, v in params.items() if v}
        
        return f"{self.base_url}?{urlencode(params)}"
    
    def _extract_job_details(self, job_element) -> Dict[str, Any]:
        """Extract job details from a job listing element"""
        try:
            # Job title
            title_element = job_element.find_element(By.CSS_SELECTOR, "h3.base-search-card__title a")
            title = title_element.text.strip() if title_element else "N/A"
            job_url = title_element.get_attribute("href") if title_element else ""
            
            # Company name
            company_element = job_element.find_element(By.CSS_SELECTOR, "h4.base-search-card__subtitle a")
            company = company_element.text.strip() if company_element else "N/A"
            
            # Location
            location_element = job_element.find_element(By.CSS_SELECTOR, "span.job-search-card__location")
            location = location_element.text.strip() if location_element else "N/A"
            
            # Date posted
            time_element = job_element.find_element(By.CSS_SELECTOR, "time.job-search-card__listdate")
            posted_date = time_element.get_attribute("datetime") if time_element else "N/A"
            
            # Job description preview (if available)
            try:
                desc_element = job_element.find_element(By.CSS_SELECTOR, "p.job-search-card__snippet")
                description_preview = desc_element.text.strip() if desc_element else ""
            except NoSuchElementException:
                description_preview = ""
            
            return {
                "title": title,
                "company": company,
                "location": location,
                "posted_date": posted_date,
                "job_url": job_url,
                "description_preview": description_preview
            }
        except Exception as e:
            print(f"Error extracting job details: {e}")
            return None
    
    def search_jobs(self, keywords: str, location: str = "", max_results: int = 25,
                   experience_level: str = "", job_type: str = "") -> List[Dict[str, Any]]:
        """
        Search for jobs on LinkedIn using keywords and filters
        
        Args:
            keywords: Job search keywords (e.g., "python developer", "data scientist")
            location: Location filter (e.g., "New York", "Remote")
            max_results: Maximum number of results to return (default: 25)
            experience_level: Experience level filter (internship, entry, associate, mid, senior, director, executive)
            job_type: Job type filter (full-time, part-time, contract, temporary, internship)
        
        Returns:
            List of job dictionaries containing job details
        """
        jobs = []
        
        try:
            # Setup driver
            self._setup_driver()
            
            # Build search URL
            search_url = self._build_search_url(keywords, location, experience_level, job_type)
            print(f"Searching LinkedIn jobs with URL: {search_url}")
            
            # Navigate to search page
            self.driver.get(search_url)
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.jobs-search__results-list")))
            
            # Add random delay to avoid being detected
            time.sleep(random.uniform(2, 4))
            
            # Find job listings
            job_elements = self.driver.find_elements(By.CSS_SELECTOR, "li.result-card.job-result-card")
            
            if not job_elements:
                # Try alternative selector
                job_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.base-card.relative")
            
            print(f"Found {len(job_elements)} job listings")
            
            # Extract job details
            for i, job_element in enumerate(job_elements[:max_results]):
                job_details = self._extract_job_details(job_element)
                if job_details:
                    jobs.append(job_details)
                    print(f"Extracted job {i+1}: {job_details['title']} at {job_details['company']}")
                
                # Add small delay between extractions
                time.sleep(random.uniform(0.5, 1.5))
            
        except TimeoutException:
            print("Timeout waiting for LinkedIn page to load")
        except Exception as e:
            print(f"Error during LinkedIn job scraping: {e}")
        finally:
            self._close_driver()
        
        return jobs
    
    def get_job_details(self, job_url: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed job information from a specific LinkedIn job URL
        
        Args:
            job_url: LinkedIn job posting URL
            
        Returns:
            Dictionary containing detailed job information
        """
        try:
            self._setup_driver()
            
            # Navigate to job page
            self.driver.get(job_url)
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.show-more-less-html__markup")))
            
            # Extract job details
            job_details = {}
            
            # Job title
            try:
                title_element = self.driver.find_element(By.CSS_SELECTOR, "h1.top-card-layout__title")
                job_details["title"] = title_element.text.strip()
            except NoSuchElementException:
                job_details["title"] = "N/A"
            
            # Company name
            try:
                company_element = self.driver.find_element(By.CSS_SELECTOR, "a.topcard__org-name-link")
                job_details["company"] = company_element.text.strip()
            except NoSuchElementException:
                job_details["company"] = "N/A"
            
            # Location
            try:
                location_element = self.driver.find_element(By.CSS_SELECTOR, "span.topcard__flavor--bullet")
                job_details["location"] = location_element.text.strip()
            except NoSuchElementException:
                job_details["location"] = "N/A"
            
            # Job description
            try:
                desc_element = self.driver.find_element(By.CSS_SELECTOR, "div.show-more-less-html__markup")
                job_details["description"] = desc_element.text.strip()
            except NoSuchElementException:
                job_details["description"] = "N/A"
            
            job_details["job_url"] = job_url
            
            return job_details
            
        except Exception as e:
            print(f"Error getting job details: {e}")
            return None
        finally:
            self._close_driver()


# Service functions for use in the API
def search_linkedin_jobs(keywords: str, location: str = "", max_results: int = 25,
                        experience_level: str = "", job_type: str = "") -> List[Dict[str, Any]]:
    """
    Search for jobs on LinkedIn using keywords
    
    Args:
        keywords: Job search keywords
        location: Location filter (optional)
        max_results: Maximum number of results (default: 25)
        experience_level: Experience level filter (optional)
        job_type: Job type filter (optional)
    
    Returns:
        List of job dictionaries
    """
    scraper = LinkedInJobScraper()
    return scraper.search_jobs(keywords, location, max_results, experience_level, job_type)


def get_linkedin_job_details(job_url: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information for a specific LinkedIn job
    
    Args:
        job_url: LinkedIn job posting URL
        
    Returns:
        Dictionary containing job details
    """
    scraper = LinkedInJobScraper()
    return scraper.get_job_details(job_url)