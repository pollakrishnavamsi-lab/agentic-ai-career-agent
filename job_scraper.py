import os
import re
import requests
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

SKILL_LIST = [
    "Python", "SQL", "Java", "C++", "Machine Learning", "Deep Learning",
    "Artificial Intelligence", "Computer Vision", "NLP", "Natural Language Processing",
    "Generative AI", "GenAI", "LLM", "RAG", "Prompt Engineering", "Agentic AI",
    "AI Agents", "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas", "NumPy",
    "OpenCV", "AWS", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes", "Git",
    "GitHub", "Spark", "Hadoop", "Databricks", "Power BI", "Tableau", "MySQL",
    "PostgreSQL", "MongoDB", "Flask", "Django", "FastAPI", "REST API", "API",
    "SQL Server", "Cybersecurity", "Data Engineering", "Data Science", "MLOps", "DevOps"
]


def extract_skills(description):
    found = []
    text = description.lower()
    for skill in SKILL_LIST:
        if re.search(r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)", text):
            found.append(skill)
    return ", ".join(found)


def extract_experience(description):
    text = description.lower()
    matches = re.findall(r"\b\d+(?:\.\d+)?\s*(?:\+|to|-)?\s*\d*\s*years?\b", text)
    if matches:
        return ", ".join(dict.fromkeys(matches))
    if "fresher" in text or "freshers" in text:
        return "Fresher"
    return "Not specified"


def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "job_agent"),
    )


def main():
    if not APP_ID or not APP_KEY:
        raise RuntimeError("Set ADZUNA_APP_ID and ADZUNA_APP_KEY in .env")
    url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
    params = {"app_id": APP_ID, "app_key": APP_KEY, "what": "AI ML Engineer", "where": "India", "results_per_page": 20}
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    db = get_db()
    cursor = db.cursor()
    check_sql = "SELECT id FROM jobs WHERE company=%s AND job_title=%s AND location=%s LIMIT 1"
    update_sql = "UPDATE jobs SET experience=%s, skills=%s, salary=%s, description=%s WHERE id=%s"
    insert_sql = "INSERT INTO jobs (company, job_title, location, experience, skills, salary, description) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    inserted = updated = 0

    for job in data.get("results", []):
        company = job.get("company", {}).get("display_name") or "Unknown"
        title = job.get("title") or "Untitled"
        location = job.get("location", {}).get("display_name") or "India"
        salary = job.get("salary_min")
        description = job.get("description") or ""
        skills = extract_skills(description)
        experience = extract_experience(description)
        cursor.execute(check_sql, (company, title, location))
        existing = cursor.fetchone()
        if existing:
            cursor.execute(update_sql, (experience, skills, salary, description, existing[0]))
            updated += 1
        else:
            cursor.execute(insert_sql, (company, title, location, experience, skills, salary, description))
            inserted += 1

    db.commit()
    cursor.close()
    db.close()
    print(f"Inserted: {inserted} | Updated: {updated}")


if __name__ == "__main__":
    main()
