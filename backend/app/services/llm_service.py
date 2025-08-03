# app/services/llm_service.py
import json
from typing import List

from openai import OpenAI
from app.core.config import DEEPSEEK_API_KEY  # <-- Import the new key
from app.core.config import GEMINI_API_KEY
import google.generativeai as genai


def analyze_job_description(description: str):
    """
    Analyzes job description using Gemini to extract key info.
    """
    if not GEMINI_API_KEY:
        raise ValueError("Gemini API key is not set. Please set the 'GEMINI_API_KEY' environment variable.")

    # Configure the Gemini API with your API key
    genai.configure(api_key=GEMINI_API_KEY)

    # Choose a Gemini model. 'gemini-pro' is a good general-purpose model for text.
    # You might consider 'gemini-1.5-pro' for more advanced use cases or longer contexts,
    # but ensure you have access to it and understand its pricing.
    model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

    prompt = f"""
    Analyze the following job description and extract key information.
    Please return the output ONLY as a JSON object with the following keys:
    - "job_title": The official job title.
    - "company_name": The name of the company hiring.
    - "key_skills": A list of the top 5-7 most important technical skills (e.g., Python, React, SQL).
    - "soft_skills": A list of the top 3-5 most important soft skills (e.g., Communication, Teamwork).
    - "experience_level": The required experience level (e.g., "Entry-level", "Mid-level", "Senior", "3-5 years").

    Job Description:
    ---
    {description}
    ---
    """

    try:
        response = model.generate_content(
            contents=[{"role": "user", "parts": [{"text": prompt}]}],
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json"  # This helps Gemini return JSON
            )
        )
        # Gemini's response is in response.text, which should be a JSON string
        analysis_result = json.loads(response.text)
        return analysis_result
    except Exception as e:
        print(f"An error occurred during LLM analysis: {e}")
        return None


def extract_job_links_from_content(content: str) -> List[str]:
    """
    Extracts individual job posting URLs from the markdown of a search results page using an LLM.
    """
    if not GEMINI_API_KEY:
        raise ValueError("Gemini API key is not set. Please set the 'GEMINI_API_KEY' environment variable.")

    genai.configure(api_key=GEMINI_API_KEY)

    # Use a fast and efficient model for this extraction task
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

    prompt = f"""
    From the provided markdown content of a job search results page, extract all the unique, fully-qualified URLs
    that lead to individual job postings.

    Return the result ONLY as a JSON object with a single key "job_urls" which contains a list of the URLs.
    Do not include any URLs that are for navigation, search filters, or company pages. Only include direct links to jobs.

    Example output format:
    {{
      "job_urls": [
        "https://www.example.com/jobs/view/12345",
        "https://www.example.com/jobs/view/67890",
        "https://www.another-site.com/careers/apply/abcde"
      ]
    }}

    Markdown Content:
    ---
    {content}
    ---
    """

    try:
        response = model.generate_content(
            contents=[{"role": "user", "parts": [{"text": prompt}]}],
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        # The response should be a JSON string like: '{"job_urls": ["url1", "url2"]}'
        result_data = json.loads(response.text)

        # Validate the structure of the returned data
        if isinstance(result_data, dict) and "job_urls" in result_data and isinstance(result_data["job_urls"], list):
            return result_data["job_urls"]
        else:
            print("LLM for link extraction returned data in an unexpected format.")
            return []  # Return empty list if format is wrong

    except Exception as e:
        print(f"An error occurred during job link extraction: {e}")
        return []  # Return empty list on error

