# app/services/llm_service.py
import json

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
