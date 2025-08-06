# app/models/job.py
import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Enum
from sqlalchemy.sql import func

from app.core.db import Base


class ApplicationStatus(enum.Enum):
    SAVED = "saved"
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    OFFER = "offer"
    REJECTED = "rejected"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String, index=True)
    company_name = Column(String, index=True)
    job_url = Column(String, unique=True, index=True)
    job_description = Column(Text)
    analysis_results = Column(JSON)  # To store skills, tone, etc. from the LLM
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.SAVED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
