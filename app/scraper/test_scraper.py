from app.scraper.naukri_scraper import scrape_jobs


jobs = scrape_jobs()

for job in jobs:
    print(job)