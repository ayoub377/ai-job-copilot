# app/schemas/linkedin_job.py

from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class LinkedInJobSearchRequest(BaseModel):
    """Request schema for LinkedIn job search"""
    keywords: str = Field(..., description="Job search keywords (e.g., 'python developer', 'data scientist')")
    location: Optional[str] = Field(None, description="Location filter (e.g., 'New York', 'Remote')")
    max_results: Optional[int] = Field(25, ge=1, le=100, description="Maximum number of results to return (1-100)")
    experience_level: Optional[str] = Field(None, description="Experience level: internship, entry, associate, mid, senior, director, executive")
    job_type: Optional[str] = Field(None, description="Job type: full-time, part-time, contract, temporary, internship")


class LinkedInJobResult(BaseModel):
    """Individual LinkedIn job result"""
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location")
    posted_date: str = Field(..., description="Date when job was posted")
    job_url: str = Field(..., description="LinkedIn job posting URL")
    description_preview: Optional[str] = Field(None, description="Brief job description preview")


class LinkedInJobSearchResponse(BaseModel):
    """Response schema for LinkedIn job search"""
    total_results: int = Field(..., description="Total number of jobs found")
    search_parameters: Dict[str, Any] = Field(..., description="Parameters used for the search")
    jobs: List[LinkedInJobResult] = Field(..., description="List of job results")
    success: bool = Field(..., description="Whether the search was successful")
    message: Optional[str] = Field(None, description="Additional message or error details")


class LinkedInJobDetailsRequest(BaseModel):
    """Request schema for getting detailed job information"""
    job_url: HttpUrl = Field(..., description="LinkedIn job posting URL")


class LinkedInJobDetails(BaseModel):
    """Detailed LinkedIn job information"""
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location")
    description: str = Field(..., description="Full job description")
    job_url: str = Field(..., description="LinkedIn job posting URL")


class LinkedInJobDetailsResponse(BaseModel):
    """Response schema for LinkedIn job details"""
    job_details: Optional[LinkedInJobDetails] = Field(None, description="Detailed job information")
    success: bool = Field(..., description="Whether the request was successful")
    message: Optional[str] = Field(None, description="Additional message or error details")