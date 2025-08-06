# app/routers/jobs.py

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.schemas.job import Job, JobCreate, JobUpdate
from app.schemas.linkedin_job import (
    LinkedInJobSearchRequest, 
    LinkedInJobSearchResponse, 
    LinkedInJobDetailsRequest, 
    LinkedInJobDetailsResponse,
    LinkedInJobResult,
    LinkedInJobDetails
)
from app.core.db import get_db
from app.services import scraper_service, llm_service
from app.services.linkedin_scraper_service import search_linkedin_jobs, get_linkedin_job_details
from app.crud.jobs import create_job, get_job, get_jobs, update_job, delete_job

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


@router.post("/linkedin/search", response_model=LinkedInJobSearchResponse, status_code=status.HTTP_200_OK)
def search_linkedin_jobs_endpoint(request: LinkedInJobSearchRequest):
    """
    Search for jobs on LinkedIn using keywords and optional filters.
    
    This endpoint scrapes LinkedIn job listings based on the provided search criteria.
    Results include job title, company, location, posting date, and job URLs.
    """
    try:
        # Call the LinkedIn scraping service
        jobs_data = search_linkedin_jobs(
            keywords=request.keywords,
            location=request.location or "",
            max_results=request.max_results or 25,
            experience_level=request.experience_level or "",
            job_type=request.job_type or ""
        )
        
        # Convert to Pydantic models
        job_results = []
        for job_data in jobs_data:
            if job_data:  # Skip any None results
                job_result = LinkedInJobResult(
                    title=job_data.get("title", "N/A"),
                    company=job_data.get("company", "N/A"),
                    location=job_data.get("location", "N/A"),
                    posted_date=job_data.get("posted_date", "N/A"),
                    job_url=job_data.get("job_url", ""),
                    description_preview=job_data.get("description_preview", "")
                )
                job_results.append(job_result)
        
        # Prepare search parameters for response
        search_params = {
            "keywords": request.keywords,
            "location": request.location,
            "max_results": request.max_results,
            "experience_level": request.experience_level,
            "job_type": request.job_type
        }
        
        # Create response
        response = LinkedInJobSearchResponse(
            total_results=len(job_results),
            search_parameters=search_params,
            jobs=job_results,
            success=True,
            message=f"Successfully found {len(job_results)} jobs matching your criteria"
        )
        
        return response
        
    except Exception as e:
        # Handle errors gracefully
        error_response = LinkedInJobSearchResponse(
            total_results=0,
            search_parameters={"keywords": request.keywords},
            jobs=[],
            success=False,
            message=f"Error searching LinkedIn jobs: {str(e)}"
        )
        return error_response


@router.post("/linkedin/details", response_model=LinkedInJobDetailsResponse, status_code=status.HTTP_200_OK)
def get_linkedin_job_details_endpoint(request: LinkedInJobDetailsRequest):
    """
    Get detailed information for a specific LinkedIn job posting.
    
    This endpoint scrapes detailed job information including the full job description
    from a LinkedIn job posting URL.
    """
    try:
        # Call the LinkedIn job details service
        job_details_data = get_linkedin_job_details(str(request.job_url))
        
        if job_details_data:
            # Convert to Pydantic model
            job_details = LinkedInJobDetails(
                title=job_details_data.get("title", "N/A"),
                company=job_details_data.get("company", "N/A"),
                location=job_details_data.get("location", "N/A"),
                description=job_details_data.get("description", "N/A"),
                job_url=job_details_data.get("job_url", str(request.job_url))
            )
            
            response = LinkedInJobDetailsResponse(
                job_details=job_details,
                success=True,
                message="Successfully retrieved job details"
            )
        else:
            response = LinkedInJobDetailsResponse(
                job_details=None,
                success=False,
                message="Could not retrieve job details from the provided URL"
            )
        
        return response
        
    except Exception as e:
        # Handle errors gracefully
        error_response = LinkedInJobDetailsResponse(
            job_details=None,
            success=False,
            message=f"Error retrieving LinkedIn job details: {str(e)}"
        )
        return error_response


@router.post("/scrape", response_model=Job, status_code=status.HTTP_201_CREATED)
def scrape_analyze_and_create_job(request: ScrapeRequest, db: Session = Depends(get_db)):
    """
    Scrapes a job URL, analyzes it with an LLM, and creates a job entry.
    """
    # Step 1: Scrape the content
    scraped_content = scraper_service.scrape_job_url(str(request.job_url))
    if not scraped_content:
        raise HTTPException(status_code=500, detail="Failed to scrape URL.")

    # Step 2: Analyze the content with the LLM
    analysis_results = llm_service.analyze_job_description(scraped_content)
    print("Gemini analysis results:", analysis_results)
    print("Type:", type(analysis_results))
    if not analysis_results:
        raise HTTPException(status_code=500, detail="Failed to analyze job description.")
    # Handle cases where analysis_results might be a list
    if isinstance(analysis_results, list):
        if analysis_results:
            # If it's a list, take the first element as the primary analysis
            # This assumes that even if multiple are returned, the first is the most relevant
            final_analysis: Dict[str, Any] = analysis_results[0]
        else:
            raise HTTPException(status_code=500, detail="LLM analysis returned an empty list.")
    elif isinstance(analysis_results, dict):
        # If it's already a dictionary, use it directly
        final_analysis: Dict[str, Any] = analysis_results
    else:
        raise HTTPException(status_code=500, detail="LLM analysis returned an unexpected type.")

    # Step 3: Create the job entry using data from the analysis
    new_job_data = JobCreate(
        job_title=analysis_results.get("job_title", "Title not found"),
        company_name=analysis_results.get("company_name", "Company not found"),
        job_url=request.job_url,
    )
    db_job = create_job(db, job=new_job_data)

    # Step 4: Add the full description and analysis JSON to the record
    db_job.job_description = scraped_content
    db_job.analysis_results = analysis_results
    db.commit()
    db.refresh(db_job)

    return db_job
