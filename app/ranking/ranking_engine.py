from app.resume.resume_parser import (
    extract_skills_from_resume
)


# Extract skills dynamically from resume
RESUME_PATH = "resume.pdf"

USER_SKILLS = extract_skills_from_resume(
    RESUME_PATH
)


PREFERRED_LOCATIONS = [
    "remote",
    "hyderabad",
    "bangalore",
    "bengaluru",
    "kolkata",
    "mumbai",
    "pune",
    "chennai"
]


def calculate_score(job):

    score = 0

    title = job.get("title", "").lower()

    company = job.get("company", "").lower()

    location = job.get("location", "").lower()

    experience = job.get("experience", "").lower()

    # =====================================
    # Resume Skill Matching
    # =====================================

    matched_skills = []

    for skill in USER_SKILLS:

        if skill.lower() in title:

            score += 15

            matched_skills.append(skill)

    # =====================================
    # Backend Role Bonus
    # =====================================

    backend_keywords = [
        "backend",
        "api",
        "developer",
        "engineer",
        "python",
        "fastapi",
        "flask",
        "django"
    ]

    for keyword in backend_keywords:

        if keyword in title:

            score += 5

    # =====================================
    # Preferred Locations
    # =====================================

    for preferred_location in PREFERRED_LOCATIONS:

        if preferred_location in location:

            score += 10

    # =====================================
    # Fresher / Lower Experience Bonus
    # =====================================

    fresher_keywords = [
        "0 to 1",
        "0-1",
        "1 to 3",
        "1-3",
        "fresher"
    ]

    for keyword in fresher_keywords:

        if keyword in experience:

            score += 10

    # =====================================
    # Top Company Bonus
    # =====================================

    top_companies = [
        "infosys",
        "tcs",
        "wipro",
        "accenture",
        "cognizant",
        "ltimindtree",
        "capgemini",
        "tech mahindra"
    ]

    for top_company in top_companies:

        if top_company in company.lower():

            score += 5

    # =====================================
    # Additional Smart Bonuses
    # =====================================

    if "remote" in location:

        score += 10

    if "hybrid" in location:

        score += 5

    # =====================================
    # Store matched skills
    # =====================================

    job["matched_skills"] = matched_skills

    return score


def rank_jobs(jobs):

    ranked_jobs = []

    for job in jobs:

        job["score"] = calculate_score(job)

        ranked_jobs.append(job)

    ranked_jobs = sorted(
        ranked_jobs,
        key=lambda x: x["score"],
        reverse=True
    )

    return ranked_jobs