# app/main.py
from fastapi import FastAPI
from app.routers import jobs

app = FastAPI(
    title="AI Job Co-pilot API",
    description="API for managing job applications and AI-powered analysis.",
    version="0.1.0"
)

app.include_router(jobs.router, prefix="/api/v1")


@app.get("/api/v1/health", tags=["Health Check"])
def health_check():
    return {"status": "ok"}
