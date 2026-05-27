from sklearn.metrics.pairwise import cosine_similarity


def calculate_similarity(
    resume_embedding,
    job_embedding
):

    similarity = cosine_similarity(
        [resume_embedding],
        [job_embedding]
    )

    return float(similarity[0][0])