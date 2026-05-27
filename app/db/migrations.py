from sqlalchemy import inspect, text

from app.db.database import engine


JOB_COLUMNS = {
    "posted_text": "VARCHAR",
    "posted_days": "INTEGER",
    "source_page": "INTEGER",
    "matched_skills": "TEXT",
    "matched_skills_count": "INTEGER DEFAULT 0",
    "semantic_score": "FLOAT DEFAULT 0",
    "freshness_score": "FLOAT DEFAULT 0",
    "weighted_skill_score": "FLOAT DEFAULT 0",
    "final_score": "FLOAT DEFAULT 0",
    "rejection_reason": "TEXT",
}


def ensure_job_columns():
    inspector = inspect(engine)

    if "jobs" not in inspector.get_table_names():
        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("jobs")
    }

    with engine.begin() as connection:
        for column_name, column_type in JOB_COLUMNS.items():
            if column_name not in existing_columns:
                connection.execute(
                    text(
                        f"ALTER TABLE jobs ADD COLUMN {column_name} {column_type}"
                    )
                )
