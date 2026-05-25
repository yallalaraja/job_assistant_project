from fastapi import APIRouter

from app.services.job_service import (
    get_jobs,
    get_top_ranked_jobs
)

from app.scraper.naukri_scraper import scrape_jobs


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


@router.get("/")
def list_jobs():

    return get_jobs()


@router.get("/top-ranked")
def top_ranked_jobs():

    return get_top_ranked_jobs()


@router.get("/scrape")
def scrape_latest_jobs():

    jobs = scrape_jobs()

    return {
        "message": "Jobs scraped successfully",
        "jobs_found": len(jobs)
    }