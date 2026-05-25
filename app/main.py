from fastapi import FastAPI

from app.routes.jobs import router as jobs_router

from app.db.database import engine, Base

# Import models
from app.models.job import Job


# Create DB tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI Job Assistant"
)

app.include_router(jobs_router)


@app.get("/")
def home():

    return {
        "message": "AI Job Assistant Backend Running"
    }