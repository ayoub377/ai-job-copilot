from sqlalchemy import Column, Integer, String, JSON
from app.core.db import Base


class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    company = Column(String)
    location = Column(String)
    raw_json = Column(JSON)  # Store structured LLM output
