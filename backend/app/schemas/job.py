# app/schemas/job.py
from pydantic import BaseModel, HttpUrl
from typing import Optional, Any
from datetime import datetime
from app.models.job import ApplicationStatus


class JobBase(BaseModel):
    job_title: str
    company_name: str
    job_url: HttpUrl


class JobCreate(JobBase):
    pass


class Job(JobBase):
    id: int
    status: ApplicationStatus
    created_at: datetime
    job_description: Optional[str] = None
    analysis_results: Optional[dict] = None

    class Config:
        from_attributes = True  # Pydantic v2


class JobUpdate(BaseModel):
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    status: Optional[ApplicationStatus] = None
