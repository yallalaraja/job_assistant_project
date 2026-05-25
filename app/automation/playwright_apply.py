from playwright.sync_api import sync_playwright
import time

def open_jobs(job_links):

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        context = browser.new_context()
        page = context.new_page()

        print("Login manually first.")
        page.goto("https://www.naukri.com")

        input("After login press ENTER...")

        for link in job_links:
            page.goto(link)
            time.sleep(5)
            print(f"Opened job: {link}")
            input("Review manually and press ENTER...")

        browser.close()