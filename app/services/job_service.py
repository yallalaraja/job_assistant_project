from app.db.database import SessionLocal
from app.models.job import Job


def get_jobs():

    db = SessionLocal()

    jobs = db.query(Job).all()

    result = []

    for job in jobs:

        result.append({
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "link": job.link,
            "score": job.score
        })

    db.close()

    return result


def get_top_ranked_jobs():

    db = SessionLocal()

    jobs = db.query(Job).order_by(
        Job.score.desc()
    ).all()

    result = []

    for job in jobs:

        result.append({
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "link": job.link,
            "score": job.score
        })

    db.close()

    return result