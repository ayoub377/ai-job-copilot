# app/routers/jobs.py

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.schemas.job import Job, JobCreate, JobUpdate
from app.core.db import get_db
from app.services import scraper_service, llm_service
from app.crud.jobs import create_job, get_job, get_jobs, update_job, delete_job
from app.models.job import Job as DBJobModel


class ScrapeRequest(BaseModel):
    job_url: HttpUrl


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs Tracker"]
)


# NOTE: The aliases from the previous fix are removed for simplicity
# as we will import the modules directly.

@router.post("/", response_model=Job, status_code=status.HTTP_201_CREATED)
def create_new_job(job: JobCreate, db: Session = Depends(get_db)):
    return create_job(db=db, job=job)


@router.get("/", response_model=List[Job])
def read_all_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    jobs = get_jobs(db, skip=skip, limit=limit)
    return jobs


@router.get("/{job_id}", response_model=Job)
def read_single_job(job_id: int, db: Session = Depends(get_db)):
    db_job = get_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job


@router.put("/{job_id}", response_model=Job)
def update_existing_job(job_id: int, job_update: JobUpdate, db: Session = Depends(get_db)):
    db_job = update_job(db, job_id=job_id, job_update=job_update)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job


@router.delete("/{job_id}", response_model=Job)
def delete_existing_job(job_id: int, db: Session = Depends(get_db)):
    db_job = delete_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job


@router.post("/scrape_and_create_jobs_refined", response_model=List[Job], status_code=status.HTTP_201_CREATED)
def scrape_analyze_and_create_jobs_refined(request: ScrapeRequest, db: Session = Depends(get_db)):
    """
    Implements a robust three-step process:
    1. Scrapes a job search results page to get its markdown.
    2. Uses an LLM to extract only the individual job URLs from the markdown.
    3. Batch-scrapes all individual job URLs for their content.
    4. Analyzes each individual job's content with an LLM to get structured data.
    5. Creates a database entry for each successfully analyzed job.
    """
    # --- Step 1: Scrape the main search results page ---
    search_page_content = scraper_service.scrape_job_url(str(request.job_url))
    if not search_page_content:
        raise HTTPException(status_code=500, detail="Failed to scrape the initial search URL.")

    # --- Step 2: Use LLM to extract only the job URLs ---
    job_urls = llm_service.extract_job_links_from_content(search_page_content)
    if not job_urls:
        raise HTTPException(status_code=404, detail="LLM could not find any job links on the page.")

    # --- Step 3: Batch-scrape all the individual job URLs ---
    individual_job_contents = scraper_service.batch_scrape_job_urls(job_urls)
    if not individual_job_contents:
        raise HTTPException(status_code=500, detail="Failed to batch-scrape individual job URLs.")

    created_jobs_in_db = []
    # --- Step 4 & 5: Analyze each job and create a DB entry ---
    for job_data in individual_job_contents:
        job_markdown = job_data.get("markdown")
        specific_job_url = job_data.get("metadata", {}).get("sourceURL")

        if not job_markdown or not specific_job_url:
            continue  # Skip if content or URL is missing

        job_analysis = llm_service.analyze_job_description(job_markdown)

        if not isinstance(job_analysis, dict):
            continue  # Skip malformed analysis

        new_job_data = JobCreate(
            job_title=job_analysis.get("job_title", "Title not found"),
            company_name=job_analysis.get("company_name", "Company not found"),
            job_url=specific_job_url
        )

        # --- FIX: Convert HttpUrl to a string before creating the DB model ---
        # Get the data as a dictionary from the Pydantic model
        job_data_for_db = new_job_data.model_dump()
        # Explicitly convert the 'job_url' field from an HttpUrl object to a string
        job_data_for_db['job_url'] = str(job_data_for_db['job_url'])
        job_data_for_db['job_description'] = job_markdown
        # Now, create the SQLAlchemy model instance with the corrected data
        db_job = DBJobModel(**job_data_for_db)

        db_job.analysis_results = job_analysis
        db.add(db_job)
        created_jobs_in_db.append(db_job)

    if not created_jobs_in_db:
        raise HTTPException(
            status_code=404,
            detail="No valid jobs were found to be created from the analysis."
        )

    db.commit()

    for job in created_jobs_in_db:
        db.refresh(job)

    return created_jobs_in_db
