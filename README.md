# AI Job Assistant

AI-powered resume-aware job discovery backend built using Python, FastAPI, Playwright, and SQLite.
The system intelligently scrapes, filters, ranks, and exposes backend engineering jobs based on resume skills and job relevance.

---

## Features

### Resume-Aware Job Matching

* Extracts skills directly from PDF resumes
* Matches jobs based on:

  * Skills
  * Backend technologies
  * Experience
  * Preferred locations
  * Company relevance
* Dynamically ranks jobs using an AI-inspired scoring engine

### Job Scraping Engine

* Built using Playwright
* Safely scrapes live job listings from Naukri
* Extracts:

  * Job Title
  * Company Name
  * Location
  * Experience
  * Job Link
* Handles duplicate prevention

### FastAPI Backend

* Modular REST API architecture
* Async-ready backend structure
* Clean separation of:

  * Routes
  * Services
  * Database layer
  * Scraper engine
  * Ranking engine

### Database Integration

* SQLite database using SQLAlchemy ORM
* Stores ranked job listings
* Prevents duplicate entries using unique job links

### Scheduler Support

* Ready for automated periodic scraping
* Can be extended for daily job updates

---

# Tech Stack

* Python
* FastAPI
* Playwright
* SQLite
* SQLAlchemy
* pdfplumber
* REST APIs
* Async Backend Architecture

---

# Project Structure

```bash
AI-Job-Assistant/
│
├── app/
│   ├── routes/
│   ├── services/
│   ├── scraper/
│   ├── ranking/
│   ├── database/
│   └── main.py
│
├── uploads/
├── resumes/
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Workflow

```text
Resume PDF
    ↓
Extract Resume Skills
    ↓
Scrape Latest Jobs
    ↓
AI Skill Matching
    ↓
Calculate Match Score
    ↓
Rank Top Jobs
    ↓
Expose Results via APIs
```

---

# Installation

## 1. Clone Repository

```bash
git clone <your-repo-url>
cd AI-Job-Assistant
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Install Playwright Browsers

```bash
playwright install
```

---

# Run the Backend

```bash
uvicorn app.main:app --reload
```

Backend will run at:

```text
http://127.0.0.1:8000
```

---

# Swagger API Docs

```text
http://127.0.0.1:8000/docs
```

---

# API Endpoints

## Scrape Latest Jobs

```http
GET /jobs/scrape
```

---

## Fetch All Jobs

```http
GET /jobs
```

---

## Fetch Top Ranked Jobs

```http
GET /jobs/top-ranked
```

---

# Resume Parsing

Supported:

* PDF resumes

Extracted skills examples:

* Python
* FastAPI
* Flask
* SQLAlchemy
* PostgreSQL
* Docker
* AWS
* JWT
* REST APIs

---

# Safe Automation Notes

* Avoid mass auto-applications
* Keep manual review in the workflow
* Avoid aggressive scraping
* Respect platform rate limits and policies
* Use automation responsibly

---

# Future Enhancements

* Full Job Description scraping
* Semantic Resume vs JD matching
* Embedding-based AI similarity scoring
* PostgreSQL migration
* Docker deployment
* Authentication system
* User profiles
* Automated scheduler jobs
* Assisted application workflow

---

# Author

Built by Raja Reddy
Backend & AI Automation Engineer
