import re

from app.ai.embeddings import generate_embedding
from app.ai.similarity import calculate_similarity
from app.resume.resume_parser import extract_skills_from_resume


RESUME_PATH = "resume.pdf"
USER_EXPERIENCE_YEARS = 3
MIN_MATCHED_SKILLS = 3

resume_data = extract_skills_from_resume(RESUME_PATH)
USER_SKILLS = [skill.lower() for skill in resume_data["skills"]]
RESUME_TEXT = resume_data["resume_text"]
SEMANTIC_SCORING_AVAILABLE = True


SKILL_ALIASES = {
    "python": ["python"],
    "fastapi": ["fastapi", "fast api"],
    "django": ["django", "django rest framework", "drf"],
    "flask": ["flask"],
    "rest api": ["rest api", "rest apis", "api development"],
    "sql": ["sql", "mysql", "postgresql", "database"],
    "postgresql": ["postgresql", "postgres"],
    "aws": ["aws", "ec2", "s3"],
    "git": ["git", "github"],
    "docker": ["docker", "container"],
    "ci/cd": ["ci/cd", "cicd", "github actions", "pipeline"],
    "redis": ["redis"],
    "celery": ["celery"],
    "jwt": ["jwt"],
    "rbac": ["rbac"],
}

SKILL_WEIGHTS = {
    "python": 30,
    "fastapi": 22,
    "django": 22,
    "flask": 18,
    "rest api": 18,
    "sql": 12,
    "postgresql": 12,
    "aws": 10,
    "docker": 10,
    "ci/cd": 8,
    "redis": 7,
    "celery": 7,
    "jwt": 5,
    "rbac": 5,
    "git": 4,
}

FRESHNESS_BONUSES = {
    0: 30,
    1: 25,
    2: 20,
    3: 15,
}

PREFERRED_ROLE_KEYWORDS = [
    "python backend",
    "backend developer",
    "backend engineer",
    "django developer",
    "fastapi developer",
    "api developer",
    "api development",
    "automation",
    "python developer",
    "software engineer",
]

SENIOR_ROLE_KEYWORDS = [
    "lead",
    "senior",
    "sr.",
    "sr ",
    "principal",
    "staff engineer",
    "architect",
    "technical lead",
    "tech lead",
    "manager",
    "engineering manager",
]

FRESHER_ROLE_KEYWORDS = [
    "fresher",
    "intern",
    "internship",
    "trainee",
    "graduate engineer trainee",
    "entry level",
]

DIVERSITY_KEYWORDS = [
    "women preferred",
    "women only",
    "diversity hiring",
    "female candidates preferred",
    "female candidate preferred",
    "returnship",
]

IRRELEVANT_KEYWORDS = [
    "sap",
    "testing only",
    "manual testing",
    "support only",
    "production support",
    "data entry",
    "bpo",
    "call center",
    "customer support",
    "technical support",
    "qa tester",
    "testing",
    "data analyst",
    "frontend",
    "front end",
    "react",
    "angular",
    "vue",
    "ai only",
    "data science",
    "machine learning engineer",
    "walk-in",
    "walkin",
    "freelancer",
    "contract only",
    "contract-only",
    "support engineer",
]

PRODUCT_COMPANY_KEYWORDS = [
    "product",
    "platform",
    "saas",
    "fintech",
    "startup",
]


def text_contains(term, text):
    pattern = rf"(?<!\w){re.escape(term)}(?!\w)"
    return re.search(pattern, text) is not None


def combined_job_text(job):
    fields = [
        job.get("title", ""),
        job.get("company", ""),
        job.get("location", ""),
        job.get("experience", ""),
        job.get("description", ""),
        job.get("posted_text", ""),
    ]
    return " ".join(fields).lower()


def extract_experience_range(experience):
    numbers = [int(number) for number in re.findall(r"\d+", experience)]

    if not numbers:
        return None, None

    if len(numbers) == 1:
        return numbers[0], numbers[0]

    return min(numbers[0], numbers[1]), max(numbers[0], numbers[1])


def is_mid_level_experience(experience):
    min_exp, max_exp = extract_experience_range(experience)

    if min_exp is None:
        return False

    return (min_exp, max_exp) in [(2, 5), (3, 5)]


def calculate_experience_bonus(experience):
    min_exp, max_exp = extract_experience_range(experience)

    if (min_exp, max_exp) == (3, 5):
        return 15

    if (min_exp, max_exp) == (2, 5):
        return 12

    return 0


def extract_posted_days(posted_text):
    text = (posted_text or "").lower()

    if any(
        term in text
        for term in [
            "today",
            "just now",
            "few hours",
            "few mins",
            "few minutes",
            "hour ago",
            "hours ago",
            "minutes ago",
        ]
    ):
        return 0

    match = re.search(r"(\d+)\s+day", text)

    if match:
        return int(match.group(1))

    return None


def calculate_freshness_score(posted_days):
    return FRESHNESS_BONUSES.get(posted_days, 0)


def get_matched_skills(job):
    text = combined_job_text(job)
    matched_skills = []

    for skill, aliases in SKILL_ALIASES.items():
        if skill not in USER_SKILLS and skill not in ["redis", "celery", "ci/cd"]:
            continue

        if any(text_contains(alias, text) for alias in aliases):
            matched_skills.append(skill)

    return matched_skills


def calculate_weighted_skill_score(matched_skills):
    return sum(SKILL_WEIGHTS.get(skill, 0) for skill in matched_skills)


def calculate_semantic_score(job):
    global SEMANTIC_SCORING_AVAILABLE

    if not SEMANTIC_SCORING_AVAILABLE:
        return 0

    description = job.get("description", "")

    if not description:
        return 0

    try:
        resume_embedding = generate_embedding(RESUME_TEXT)
        job_embedding = generate_embedding(description)
        similarity = calculate_similarity(resume_embedding, job_embedding)
        return round(similarity * 35, 2)

    except Exception as exc:
        SEMANTIC_SCORING_AVAILABLE = False
        print(f"Semantic scoring failed: {exc}")
        return 0


def has_any_keyword(keywords, text):
    return any(keyword in text for keyword in keywords)


def evaluate_job(job):
    text = combined_job_text(job)
    title = job.get("title", "").lower()
    experience = job.get("experience", "")
    posted_days = extract_posted_days(job.get("posted_text", ""))
    matched_skills = get_matched_skills(job)
    weighted_skill_score = calculate_weighted_skill_score(matched_skills)
    freshness_score = calculate_freshness_score(posted_days)
    experience_bonus = calculate_experience_bonus(experience)
    product_company_bonus = 0
    rejection_reasons = []

    if posted_days is None or posted_days > 3:
        rejection_reasons.append("job is not fresh")

    if not is_mid_level_experience(experience):
        rejection_reasons.append("experience range is not mid-level")

    if has_any_keyword(SENIOR_ROLE_KEYWORDS, title):
        rejection_reasons.append("senior/lead role")

    if has_any_keyword(FRESHER_ROLE_KEYWORDS, text):
        rejection_reasons.append("fresher/internship role")

    if has_any_keyword(DIVERSITY_KEYWORDS, text):
        rejection_reasons.append("women-only/diversity hiring role")

    if has_any_keyword(IRRELEVANT_KEYWORDS, text):
        rejection_reasons.append("irrelevant non-development role")

    if len(matched_skills) < MIN_MATCHED_SKILLS:
        rejection_reasons.append("less than 3 matching skills")

    if not has_any_keyword(PREFERRED_ROLE_KEYWORDS, text):
        rejection_reasons.append("role is not backend/API focused")

    if has_any_keyword(PRODUCT_COMPANY_KEYWORDS, text):
        product_company_bonus = 8

    semantic_score = 0

    if not rejection_reasons:
        semantic_score = calculate_semantic_score(job)

    final_score = round(
        (
            (semantic_score * 2)
            + weighted_skill_score
            + freshness_score
            + experience_bonus
            + product_company_bonus
        ),
        2,
    )

    result = {
        "accepted": len(rejection_reasons) == 0,
        "rejection_reasons": rejection_reasons,
        "rejection_reason": "; ".join(rejection_reasons),
        "matched_skills": matched_skills,
        "matched_skills_count": len(matched_skills),
        "weighted_skill_score": weighted_skill_score,
        "semantic_score": semantic_score,
        "freshness_score": freshness_score,
        "experience_bonus": experience_bonus,
        "product_company_bonus": product_company_bonus,
        "final_score": final_score,
        "score": final_score,
        "posted_days": posted_days,
    }

    job.update(result)
    return result


def calculate_score(job):
    return evaluate_job(job)["final_score"]


def rank_jobs(jobs):
    ranked_jobs = []

    for job in jobs:
        evaluation = evaluate_job(job)

        if evaluation["accepted"]:
            ranked_jobs.append(job)

    return sorted(
        ranked_jobs,
        key=lambda item: (
            item["final_score"],
            item["freshness_score"],
            item["weighted_skill_score"],
            -abs(
                USER_EXPERIENCE_YEARS
                - (extract_experience_range(item.get("experience", ""))[0] or USER_EXPERIENCE_YEARS)
            ),
        ),
        reverse=True,
    )
