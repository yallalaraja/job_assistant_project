from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from app.db.database import Base


class Job(Base):

    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String)

    link = Column(String, unique=True)

    company = Column(String, nullable=True)

    location = Column(String, nullable=True)

    score = Column(Integer, default=0)