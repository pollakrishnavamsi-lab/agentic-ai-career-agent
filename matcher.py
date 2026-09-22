import math
import re
from db import fetch_jobs


# ---------------------------------------------------------
# NORMALIZATION
# ---------------------------------------------------------

def normalize(value):
    return re.sub(
        r"[^a-z0-9+#.]",
        " ",
        str(value).lower()
    ).strip()


def skill_set(value):
    return {
        normalize(x)
        for x in str(value or "").split(",")
        if x.strip()
    }


# ---------------------------------------------------------
# LOAD SENTENCE TRANSFORMER ONLY ONCE
# ---------------------------------------------------------

_MODEL = None


def get_model():
    """
    Loads the SentenceTransformer model only once.

    Previously the model was loaded for every single job,
    which made resume analysis extremely slow.
    """

    global _MODEL

    if _MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer

            print("Loading semantic matching model...")
            _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
            print("Semantic matching model loaded successfully.")

        except Exception as e:
            print("Could not load SentenceTransformer:", e)
            _MODEL = False

    return _MODEL


# ---------------------------------------------------------
# FALLBACK SEMANTIC SIMILARITY
# ---------------------------------------------------------

def token_similarity(text_a, text_b):

    a = set(
        re.findall(
            r"[a-zA-Z][a-zA-Z+#.-]{1,}",
            str(text_a).lower()
        )
    )

    b = set(
        re.findall(
            r"[a-zA-Z][a-zA-Z+#.-]{1,}",
            str(text_b).lower()
        )
    )

    if not a or not b:
        return 0.0

    return len(a & b) / math.sqrt(len(a) * len(b))


# ---------------------------------------------------------
# SEMANTIC SIMILARITY
# ---------------------------------------------------------

def semantic_similarity(text_a, text_b):

    model = get_model()

    # If model failed to load, use token similarity
    if model is False:
        return token_similarity(text_a, text_b)

    try:

        embeddings = model.encode(
            [text_a, text_b],
            normalize_embeddings=True
        )

        similarity = float(
            embeddings[0] @ embeddings[1]
        )

        return similarity

    except Exception as e:

        print("Semantic similarity error:", e)

        return token_similarity(text_a, text_b)


# ---------------------------------------------------------
# OPTIMIZED BATCH SEMANTIC SIMILARITY
# ---------------------------------------------------------

def batch_semantic_similarity(resume_text, job_texts):

    model = get_model()

    # Fallback if model is unavailable
    if model is False:

        return [
            token_similarity(resume_text, job_text)
            for job_text in job_texts
        ]

    try:

        # Encode resume only once
        resume_embedding = model.encode(
            [resume_text],
            normalize_embeddings=True
        )[0]

        # Encode ALL jobs together
        job_embeddings = model.encode(
            job_texts,
            normalize_embeddings=True,
            batch_size=16,
            show_progress_bar=False
        )

        similarities = job_embeddings @ resume_embedding

        return [
            float(score)
            for score in similarities
        ]

    except Exception as e:

        print("Batch semantic matching error:", e)

        return [
            token_similarity(resume_text, job_text)
            for job_text in job_texts
        ]


# ---------------------------------------------------------
# MAIN JOB RANKING
# ---------------------------------------------------------

def rank_jobs(profile, limit=10):

    jobs = fetch_jobs()

    if not jobs:
        return []

    resume_skills = {
        normalize(skill)
        for skill in profile.get("skills", [])
    }

    resume_text = profile.get("raw_text", "")

    # -----------------------------------------------------
    # REMOVE DUPLICATE JOBS
    # -----------------------------------------------------

    unique_jobs = []
    seen = set()

    for job in jobs:

        key = (
            str(job.get("company", "")).strip().lower(),
            str(job.get("job_title", "")).strip().lower(),
            str(job.get("location", "")).strip().lower()
        )

        if key in seen:
            continue

        seen.add(key)
        unique_jobs.append(job)

    print(
        f"Jobs loaded: {len(jobs)} | "
        f"Unique jobs: {len(unique_jobs)}"
    )

    # -----------------------------------------------------
    # PREPARE JOB TEXT
    # -----------------------------------------------------

    job_texts = []

    for job in unique_jobs:

        job_text = (
            f"{job.get('job_title', '')} "
            f"{job.get('skills', '')} "
            f"{job.get('description', '')}"
        )

        job_texts.append(job_text)

    # -----------------------------------------------------
    # CALCULATE SEMANTIC SIMILARITY IN BATCH
    # -----------------------------------------------------

    semantic_scores = batch_semantic_similarity(
        resume_text,
        job_texts
    )

    # -----------------------------------------------------
    # CALCULATE FINAL SCORES
    # -----------------------------------------------------

    results = []

    for index, job in enumerate(unique_jobs):

        job_skills = skill_set(
            job.get("skills")
        )

        matched = sorted(
            resume_skills & job_skills
        )

        missing = sorted(
            job_skills - resume_skills
        )

        # Skill matching score
        if job_skills:

            skill_score = (
                len(matched)
                / len(job_skills)
                * 100
            )

        else:

            skill_score = 0

        # Semantic score
        semantic_score = (
            semantic_scores[index] * 100
        )

        # Keep score between 0 and 100
        semantic_score = max(
            0,
            min(100, semantic_score)
        )

        # -------------------------------------------------
        # FINAL HYBRID SCORE
        # -------------------------------------------------
        #
        # 60% exact skill matching
        # 40% semantic similarity
        #

        final_score = (
            skill_score * 0.60
            +
            semantic_score * 0.40
        )

        results.append({

            "id": job.get("id"),

            "company": job.get("company"),

            "title": job.get("job_title"),

            "location": job.get("location"),

            "experience": job.get("experience"),

            "salary": job.get("salary"),

            "matched_skills": matched,

            "missing_skills": missing[:10],

            "skill_score": round(
                skill_score,
                2
            ),

            "semantic_score": round(
                semantic_score,
                2
            ),

            "match_percentage": round(
                final_score,
                2
            ),
        })

    # -----------------------------------------------------
    # SORT BEST MATCH FIRST
    # -----------------------------------------------------

    results.sort(
        key=lambda x: x["match_percentage"],
        reverse=True
    )

    return results[:limit]