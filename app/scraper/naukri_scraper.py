import random
import time
from functools import partial
from pathlib import Path
from tempfile import mkdtemp
from urllib.parse import quote_plus, urlencode

from sqlalchemy.exc import SQLAlchemyError
from playwright.sync_api import sync_playwright

from app.db.database import SessionLocal
from app.models.job import Job
from app.ranking.ranking_engine import evaluate_job


print = partial(print, flush=True)

SEARCH_QUERIES = [
    "Python Developer",
    "Backend Developer Python",
    "Django Developer",
    "FastAPI Developer",
]

PREFERRED_LOCATIONS = [
    "Bangalore",
    "Hyderabad",
    "Pune",
    "Chennai",
]

MAX_ACCEPTED_JOBS = 50
MAX_PAGES_PER_SEARCH = 20
MAX_JOBS_PER_PAGE = 20
PAGE_LOAD_RETRIES = 2
DUPLICATE_PAGE_STOP_RATIO = 0.85
NAUKRI_HOME_URL = "https://www.naukri.com/"
USER_DATA_DIR = Path(".naukri_browser_profile")

JOB_CARD_SELECTORS = [
    "div.cust-job-tuple",
    "article.jobTuple",
    "div.jobTuple",
    "div.srp-jobtuple-wrapper",
    "div[class*='jobTuple']",
    "div[class*='job-tuple']",
    "article:has(a[href*='job-listings'])",
    "div:has(> div > a[href*='job-listings'])",
]

DESCRIPTION_SELECTORS = [
    ".styles_JDC__dang-inner-html__h0K4t",
    "section.styles_job-desc-container__txpYf",
    ".job-desc",
]

POSTED_SELECTORS = [
    ".job-post-day",
    "span.job-post-day",
    ".styles_jhc__stat__PgY67",
    ".styles_job-meta__U3T2W span",
    "span:has-text('Today')",
    "span:has-text('today')",
    "span:has-text('day ago')",
    "span:has-text('days ago')",
    "span:has-text('hour ago')",
    "span:has-text('hours ago')",
]


def random_wait(min_seconds=0.8, max_seconds=2.2):
    time.sleep(random.uniform(min_seconds, max_seconds))


def slugify_keyword(keyword):
    return quote_plus(keyword.lower()).replace("+", "-")


def build_search_url(keyword, page_number):
    slug = slugify_keyword(keyword)
    page_suffix = "" if page_number == 1 else f"-{page_number}"
    params = {
        "k": keyword,
        "l": ",".join(PREFERRED_LOCATIONS),
        "experience": "2-5",
        "jobAge": "3",
        "sort": "date",
        "src": "sortby",
    }

    return (
        f"https://www.naukri.com/{slug}-jobs{page_suffix}"
        f"?{urlencode(params)}"
    )


def build_fallback_search_url(keyword, page_number):
    page_suffix = "" if page_number == 1 else f"-{page_number}"
    params = {
        "k": keyword,
        "l": ",".join(PREFERRED_LOCATIONS),
        "experience": "2-5",
        "jobAge": "3",
        "sort": "date",
        "src": "sortby",
    }

    return (
        f"https://www.naukri.com/jobs-in-india{page_suffix}"
        f"?{urlencode(params)}"
    )


def safe_text(locator, default=""):
    try:
        return locator.inner_text().strip()
    except Exception:
        return default


def safe_attribute(locator, attribute, default=""):
    try:
        return locator.get_attribute(attribute) or default
    except Exception:
        return default


def first_text(parent, selectors, default=""):
    for selector in selectors:
        try:
            text = parent.locator(selector).first.inner_text().strip()

            if text:
                return text

        except Exception:
            continue

    return default


def find_posted_text(card):
    posted_text = first_text(
        card,
        POSTED_SELECTORS,
        default="",
    )

    if posted_text:
        return posted_text

    card_text = safe_text(card).lower()

    for marker in [
        "today",
        "just now",
        "few hours ago",
        "1 day ago",
        "2 days ago",
        "3 days ago",
    ]:
        if marker in card_text:
            return marker

    return ""


def goto_with_retry(page, url):
    for attempt in range(1, PAGE_LOAD_RETRIES + 1):
        try:
            page.goto(
                url,
                timeout=60000,
                wait_until="domcontentloaded",
            )
            return True

        except Exception as exc:
            print(f"Page load failed, attempt {attempt}: {exc}")
            random_wait(2.0, 4.0)

    return False


def is_access_denied(page):
    try:
        title = page.title().lower()
        body = page.locator("body").inner_text(timeout=3000).lower()
        return "access denied" in title or "access denied" in body

    except Exception:
        return False


def warm_up_naukri(page):
    print("Opening Naukri homepage for browser warm-up...")

    if not goto_with_retry(page, NAUKRI_HOME_URL):
        print("Naukri homepage warm-up failed.")
        return False

    random_wait(4.0, 7.0)
    log_page_diagnostics(page)

    if is_access_denied(page):
        print("Naukri returned Access Denied on homepage warm-up.")
        return False

    return True


def goto_search_page(page, url):
    if not goto_with_retry(page, url):
        return False

    random_wait(2.0, 4.0)

    if not is_access_denied(page):
        return True

    print("Access Denied detected. Retrying after Naukri homepage warm-up...")

    if not warm_up_naukri(page):
        return True

    if not goto_with_retry(page, url):
        return False

    random_wait(2.0, 4.0)
    return True


def log_page_diagnostics(page):
    try:
        print(f"Loaded page title: {page.title()}")
        print(f"Current URL: {page.url}")
    except Exception as exc:
        print(f"Could not read page diagnostics: {exc}")


def get_job_cards(page):
    selector_counts = []

    for selector in JOB_CARD_SELECTORS:
        try:
            locator = page.locator(selector)
            count = locator.count()
            selector_counts.append(f"{selector}={count}")

            if count:
                print(f"Using job card selector: {selector} ({count})")
                return locator.all()

        except Exception:
            selector_counts.append(f"{selector}=error")

    print("No job card selector matched.")
    print("Selector diagnostics: " + " | ".join(selector_counts))

    try:
        print(f"Page body preview: {page.locator('body').inner_text(timeout=3000)[:500]}")
    except Exception as exc:
        print(f"Could not capture page body preview: {exc}")

    return []


def scrape_job_description(browser, link):
    if not link:
        return ""

    job_page = browser.new_page()

    try:
        if not goto_with_retry(job_page, link):
            return ""

        random_wait(0.8, 1.8)

        return first_text(
            job_page,
            DESCRIPTION_SELECTORS,
            default="",
        )

    except Exception as exc:
        print(f"JD scrape failed: {exc}")
        return ""

    finally:
        job_page.close()


def extract_job_card(card, browser, keyword, page_number):
    title_locator = card.locator(
        "a.title, a[href*='job-listings']"
    ).first
    title = safe_text(title_locator)
    link = safe_attribute(title_locator, "href")

    company = safe_text(
        card.locator("a.comp-name, a[class*='comp-name']").first,
        default="Unknown",
    )

    location = safe_text(
        card.locator("span.locWdth, span[class*='loc']").first,
        default="Unknown",
    )

    experience = safe_text(
        card.locator("span.expwdth, span[class*='exp']").first,
        default="",
    )

    posted_text = find_posted_text(card)
    description = scrape_job_description(browser, link)

    return {
        "title": title,
        "company": company,
        "location": location,
        "experience": experience,
        "posted_text": posted_text,
        "description": description,
        "link": link,
        "source_keyword": keyword,
        "source_page": page_number,
    }


def log_rejection(job_data, rejection_reasons):
    print(f"Rejected: {job_data.get('title', 'Unknown title')}")
    print("Reason:")

    for reason in rejection_reasons:
        print(f"- {reason}")


def build_job_model(job_data):
    return Job(
        title=job_data["title"],
        company=job_data["company"],
        location=job_data["location"],
        experience=job_data["experience"],
        posted_text=job_data["posted_text"],
        posted_days=job_data["posted_days"],
        source_page=job_data["source_page"],
        description=job_data["description"],
        skills_required=", ".join(job_data["matched_skills"]),
        matched_skills=", ".join(job_data["matched_skills"]),
        matched_skills_count=job_data["matched_skills_count"],
        link=job_data["link"],
        score=job_data["final_score"],
        semantic_score=job_data["semantic_score"],
        freshness_score=job_data["freshness_score"],
        weighted_skill_score=job_data["weighted_skill_score"],
        final_score=job_data["final_score"],
        rejection_reason=job_data.get("rejection_reason", ""),
    )


def save_job_immediately(job_data):
    db = SessionLocal()

    try:
        existing_job = db.query(Job).filter(
            Job.link == job_data["link"]
        ).first()

        if existing_job:
            print(f"Duplicate skipped: {job_data['title']}")
            return "duplicate"

        db.add(build_job_model(job_data))
        db.commit()
        print(f"Saved to DB: {job_data['title']}")
        return "saved"

    except SQLAlchemyError as exc:
        db.rollback()
        print(f"DB error for {job_data.get('title', 'Unknown title')}: {exc}")
        return "error"

    finally:
        db.close()


def create_stats():
    return {
        "pages_visited": 0,
        "jobs_scanned": 0,
        "accepted_jobs": 0,
        "rejected_jobs": 0,
        "duplicates_skipped": 0,
        "db_inserts_successful": 0,
        "db_errors": 0,
    }


def should_stop(stats):
    return stats["accepted_jobs"] >= MAX_ACCEPTED_JOBS


def scrape_search(browser, page, keyword, seen_links, stats, max_pages):
    accepted_jobs = []
    page_number = 1

    while page_number <= max_pages and not should_stop(stats):
        url = build_search_url(keyword, page_number)
        print(f"Page traversal: keyword='{keyword}' page={page_number}")
        print(url)

        if not goto_search_page(page, url):
            break

        stats["pages_visited"] += 1
        log_page_diagnostics(page)

        if is_access_denied(page):
            fallback_url = build_fallback_search_url(keyword, page_number)
            print("Primary search URL is blocked. Trying fallback search URL:")
            print(fallback_url)

            if not goto_search_page(page, fallback_url):
                break

            log_page_diagnostics(page)

        if is_access_denied(page):
            print("Access Denied still active. Stopping this search.")
            break

        cards = get_job_cards(page)

        if not cards:
            print(f"No jobs found on page {page_number}. Stopping this search.")
            break

        duplicate_count = 0
        page_links = []
        print(f"Jobs found on page: {len(cards)}")
        print(f"Accepted jobs count: {stats['accepted_jobs']}")

        for card in cards[:MAX_JOBS_PER_PAGE]:
            if should_stop(stats):
                break

            try:
                job_data = extract_job_card(
                    card,
                    browser,
                    keyword,
                    page_number,
                )

                if not job_data["link"]:
                    print("Rejected: missing job link")
                    stats["rejected_jobs"] += 1
                    continue

                page_links.append(job_data["link"])

                if job_data["link"] in seen_links:
                    duplicate_count += 1
                    stats["duplicates_skipped"] += 1
                    print(f"Duplicate skipped: {job_data['title']}")
                    continue

                seen_links.add(job_data["link"])
                stats["jobs_scanned"] += 1

                evaluation = evaluate_job(job_data)

                if not evaluation["accepted"]:
                    stats["rejected_jobs"] += 1
                    log_rejection(
                        job_data,
                        evaluation["rejection_reasons"],
                    )
                    continue

                print(
                    "Accepted: "
                    f"{job_data['title']} | "
                    f"Score: {job_data['final_score']} | "
                    f"Skills: {job_data['matched_skills_count']} | "
                    f"Freshness: {job_data['posted_text']}"
                )

                save_status = save_job_immediately(job_data)

                if save_status == "saved":
                    stats["accepted_jobs"] += 1
                    stats["db_inserts_successful"] += 1
                    accepted_jobs.append(job_data)

                elif save_status == "duplicate":
                    stats["duplicates_skipped"] += 1

                else:
                    stats["db_errors"] += 1

            except Exception as exc:
                stats["rejected_jobs"] += 1
                print(f"Error processing card: {exc}")

        if page_links and duplicate_count / len(page_links) >= DUPLICATE_PAGE_STOP_RATIO:
            print("Duplicate-heavy page detected. Stopping this search.")
            break

        page_number += 1
        random_wait(1.5, 3.0)

    return accepted_jobs


def print_summary(stats):
    print("Final scrape summary")
    print(f"Total pages visited: {stats['pages_visited']}")
    print(f"Total jobs scanned: {stats['jobs_scanned']}")
    print(f"Total accepted jobs: {stats['accepted_jobs']}")
    print(f"Total rejected jobs: {stats['rejected_jobs']}")
    print(f"Total duplicates skipped: {stats['duplicates_skipped']}")
    print(f"Total DB inserts successful: {stats['db_inserts_successful']}")
    print(f"Total DB errors: {stats['db_errors']}")


def create_browser_context(playwright, headless):
    USER_DATA_DIR.mkdir(exist_ok=True)
    print(f"Launching Chrome. headless={headless}")
    print(f"Browser profile: {USER_DATA_DIR.resolve()}")

    launch_options = {
        "user_data_dir": str(USER_DATA_DIR),
        "headless": headless,
        "slow_mo": 100,
        "viewport": {"width": 1366, "height": 768},
        "locale": "en-IN",
        "timezone_id": "Asia/Kolkata",
        "user_agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "extra_http_headers": {
            "Accept-Language": "en-IN,en;q=0.9",
        },
        "args": [
            "--start-maximized",
        ],
    }

    try:
        context = playwright.chromium.launch_persistent_context(
            channel="chrome",
            **launch_options,
        )

    except Exception as exc:
        fallback_profile = mkdtemp(prefix="naukri_playwright_")
        print(f"Chrome launch failed: {exc}")
        print(f"Retrying with bundled Chromium profile: {fallback_profile}")
        launch_options["user_data_dir"] = fallback_profile
        context = playwright.chromium.launch_persistent_context(
            **launch_options,
        )

    context.set_default_timeout(15000)
    context.set_default_navigation_timeout(45000)
    print("Browser launched successfully.")

    return context


def scrape_jobs(
    max_pages=MAX_PAGES_PER_SEARCH,
    headless=False,
    debug_pause_seconds=0,
):
    accepted_jobs = []
    seen_links = set()
    stats = create_stats()
    print("Starting Naukri scrape...")
    print(f"Max pages per search: {max_pages}")
    print(f"Max accepted jobs: {MAX_ACCEPTED_JOBS}")

    with sync_playwright() as playwright:
        browser = create_browser_context(
            playwright=playwright,
            headless=headless,
        )

        page = browser.new_page()
        warm_up_naukri(page)

        for keyword in SEARCH_QUERIES:
            if should_stop(stats):
                break

            accepted_jobs.extend(
                scrape_search(
                    browser=browser,
                    page=page,
                    keyword=keyword,
                    seen_links=seen_links,
                    stats=stats,
                    max_pages=max_pages,
                )
            )

            random_wait(2.0, 4.0)

        if debug_pause_seconds:
            print(
                "Debug pause: browser will stay open for "
                f"{debug_pause_seconds} seconds."
            )
            time.sleep(debug_pause_seconds)

        browser.close()

    accepted_jobs = sorted(
        accepted_jobs,
        key=lambda job: (
            job["final_score"],
            job["freshness_score"],
            job["weighted_skill_score"],
            job["semantic_score"],
        ),
        reverse=True,
    )

    print_summary(stats)

    return accepted_jobs
