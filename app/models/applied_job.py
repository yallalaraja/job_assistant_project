from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.db.database import Base


class AppliedJob(Base):
    __tablename__ = "applied_jobs"

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)

    title = Column(String)

    company = Column(String)

    link = Column(String, unique=True)

    status = Column(String, default="pending")

    final_score = Column(Float, default=0.0)

    notes = Column(Text)

    applied_at = Column(DateTime(timezone=True), server_default=func.now())
