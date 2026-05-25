from playwright.sync_api import sync_playwright
import time

from app.db.database import SessionLocal
from app.models.job import Job

from app.ranking.ranking_engine import calculate_score


def scrape_jobs():

    jobs = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            channel="chrome",
            headless=False,
            slow_mo=500
        )

        page = browser.new_page()

        page.goto(
            "https://www.naukri.com/python-developer-jobs",
            timeout=60000
        )

        # Wait for page to fully render
        time.sleep(5)

        print("Page loaded successfully")

        # Updated selector
        cards = page.locator("div.cust-job-tuple").all()

        print(f"Found {len(cards)} job cards")

        for card in cards[:10]:

            try:

                print("Processing job card...")

                # Title
                title = card.locator(
                    "a.title"
                ).inner_text().strip()

                # Link
                link = card.locator(
                    "a.title"
                ).get_attribute("href")

                # Company
                try:
                    company = card.locator(
                        "a.comp-name"
                    ).inner_text().strip()

                except:
                    company = "Unknown"

                # Location
                try:
                    location = card.locator(
                        "span.locWdth"
                    ).first.inner_text().strip()

                except:
                    location = "Unknown"

                # Experience
                try:
                    experience = card.locator(
                        "span.expwdth"
                    ).inner_text().strip()

                except:
                    experience = ""

                # Prepare job data
                job_data = {
                    "title": title,
                    "company": company,
                    "location": location,
                    "experience": experience,
                    "link": link
                }

                # Calculate score
                score = calculate_score(job_data)

                job_data["score"] = score

                jobs.append(job_data)

                print(job_data)

            except Exception as e:

                print(f"Error processing card: {e}")

        browser.close()

    # Save jobs into database
    db = SessionLocal()

    for job_data in jobs:

        existing_job = db.query(Job).filter(
            Job.link == job_data["link"]
        ).first()

        if not existing_job:

            new_job = Job(
                title=job_data["title"],
                link=job_data["link"],
                company=job_data["company"],
                location=job_data["location"],
                score=job_data["score"]
            )

            db.add(new_job)

            print(f"Saved: {job_data['title']}")

        else:

            print(f"Already exists: {job_data['title']}")

    db.commit()

    db.close()

    print(f"Total jobs collected: {len(jobs)}")

    return jobs