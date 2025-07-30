# app/routers/jobs.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud  # <-- Import crud
from app.schemas.job import Job, JobCreate, JobUpdate
from app.core.db import get_db

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs Tracker"]
)


# NOTE: The aliases from the previous fix are removed for simplicity
# as we will import the modules directly.

@router.post("/", response_model=Job, status_code=status.HTTP_201_CREATED)
def create_new_job(job: JobCreate, db: Session = Depends(get_db)):
    return crud.jobs.create_job(db=db, job=job)


@router.get("/", response_model=List[Job])
def read_all_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    jobs = crud.jobs.get_jobs(db, skip=skip, limit=limit)
    return jobs


@router.get("/{job_id}", response_model=Job)
def read_single_job(job_id: int, db: Session = Depends(get_db)):
    db_job = crud.jobs.get_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job


@router.put("/{job_id}", response_model=Job)
def update_existing_job(job_id: int, job_update: JobUpdate, db: Session = Depends(get_db)):
    db_job = crud.jobs.update_job(db, job_id=job_id, job_update=job_update)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job


@router.delete("/{job_id}", response_model=Job)
def delete_existing_job(job_id: int, db: Session = Depends(get_db)):
    db_job = crud.jobs.delete_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job
