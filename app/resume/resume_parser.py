import pdfplumber
import re


KNOWN_SKILLS = [
    "python",
    "fastapi",
    "flask",
    "django",
    "django rest framework",
    "postgresql",
    "mysql",
    "sqlalchemy",
    "docker",
    "aws",
    "jwt",
    "rbac",
    "rest api",
    "rest apis",
    "webhooks",
    "razorpay",
    "git",
    "github",
    "github actions",
    "linux",
    "postman",
    "jsonb",
    "sql",
    "concurrency",
    "row-level locking"
]


def extract_resume_text(pdf_path):

    text = ""

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:

                text += page_text + "\n"

    return text.lower()


def extract_skills_from_resume(pdf_path):

    text = extract_resume_text(pdf_path)

    extracted_skills = set()

    for skill in KNOWN_SKILLS:

        pattern = rf"\b{re.escape(skill)}\b"

        if re.search(pattern, text):

            extracted_skills.add(skill)

    return list(extracted_skills)