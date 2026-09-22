import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "job_agent")
    )


def fetch_jobs():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                id,
                job_title AS title,
                company,
                location,
                experience,
                skills,
                salary
            FROM jobs
            ORDER BY id DESC
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def search_jobs(query=""):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        query = (query or "").strip()

        if not query:

            cursor.execute("""
                SELECT
                    id,
                    job_title AS title,
                    company,
                    location,
                    experience,
                    skills,
                    salary
                FROM jobs
                ORDER BY id DESC
                LIMIT 20
            """)

        else:

            search_value = f"%{query}%"

            cursor.execute("""
                SELECT
                    id,
                    job_title AS title,
                    company,
                    location,
                    experience,
                    skills,
                    salary
                FROM jobs
                WHERE
                    job_title LIKE %s
                    OR company LIKE %s
                    OR location LIKE %s
                    OR skills LIKE %s
                    OR experience LIKE %s
                ORDER BY id DESC
                LIMIT 20
            """, (
                search_value,
                search_value,
                search_value,
                search_value,
                search_value
            ))

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()