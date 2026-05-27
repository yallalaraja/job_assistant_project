from app.scraper.naukri_scraper import scrape_jobs


jobs = scrape_jobs(
    max_pages=2,
    headless=False,
    debug_pause_seconds=90,
)

for job in jobs:
    print(job)
