from sqlalchemy import Column, Integer, String, Float, Text
from app.db.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String)
    company = Column(String)
    location = Column(String)

    experience = Column(String)

    posted_text = Column(String)

    posted_days = Column(Integer)

    source_page = Column(Integer)

    description = Column(Text)

    skills_required = Column(Text)

    matched_skills = Column(Text)

    matched_skills_count = Column(Integer, default=0)

    link = Column(String, unique=True)

    score = Column(Float, default=0.0)

    semantic_score = Column(Float, default=0.0)

    freshness_score = Column(Float, default=0.0)

    weighted_skill_score = Column(Float, default=0.0)

    final_score = Column(Float, default=0.0)

    rejection_reason = Column(Text)
