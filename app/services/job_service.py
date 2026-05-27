from app.db.database import SessionLocal
from app.models.job import Job


MIN_VISIBLE_SCORE = 70


def get_jobs():

    db = SessionLocal()

    jobs = db.query(Job).filter(
        Job.final_score >= MIN_VISIBLE_SCORE
    ).order_by(
        Job.final_score.desc(),
        Job.freshness_score.desc(),
        Job.weighted_skill_score.desc()
    ).all()

    result = []

    for job in jobs:

        result.append({
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "experience": job.experience,
            "posted_days": job.posted_days,
            "posted_text": job.posted_text,
            "source_page": job.source_page,
            "link": job.link,
            "score": job.score,
            "semantic_score": job.semantic_score,
            "freshness_score": job.freshness_score,
            "matched_skills": job.matched_skills,
            "matched_skills_count": job.matched_skills_count,
            "weighted_skill_score": job.weighted_skill_score,
            "final_score": job.final_score,
            "rejection_reason": job.rejection_reason
        })

    db.close()

    return result


def get_top_ranked_jobs():

    db = SessionLocal()

    jobs = db.query(Job).filter(
        Job.final_score >= MIN_VISIBLE_SCORE
    ).order_by(
        Job.final_score.desc(),
        Job.freshness_score.desc(),
        Job.weighted_skill_score.desc()
    ).all()

    result = []

    for job in jobs:

        result.append({
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "experience": job.experience,
            "posted_days": job.posted_days,
            "posted_text": job.posted_text,
            "source_page": job.source_page,
            "link": job.link,
            "score": job.score,
            "semantic_score": job.semantic_score,
            "freshness_score": job.freshness_score,
            "matched_skills": job.matched_skills,
            "matched_skills_count": job.matched_skills_count,
            "weighted_skill_score": job.weighted_skill_score,
            "final_score": job.final_score,
            "rejection_reason": job.rejection_reason
        })

    db.close()

    return result
