# app/crud/jobs.py

from sqlalchemy.orm import Session
from app import models, schemas


def get_job(db: Session, job_id: int):
    return db.query(models.job.Job).filter(models.job.Job.id == job_id).first()


def get_jobs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.job.Job).offset(skip).limit(limit).all()


def create_job(db: Session, job: schemas.job.JobCreate):
    db_job = models.job.Job(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


def update_job(db: Session, job_id: int, job_update: schemas.job.JobUpdate):
    db_job = get_job(db, job_id)
    if not db_job:
        return None

    update_data = job_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_job, key, value)

    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


def delete_job(db: Session, job_id: int):
    db_job = get_job(db, job_id)
    if not db_job:
        return None
    db.delete(db_job)
    db.commit()
    return db_job