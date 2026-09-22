CREATE DATABASE IF NOT EXISTS job_agent;
USE job_agent;

CREATE TABLE IF NOT EXISTS jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company VARCHAR(255),
    job_title VARCHAR(255),
    location VARCHAR(255),
    experience VARCHAR(100),
    skills TEXT,
    salary VARCHAR(100),
    description LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_title (job_title),
    INDEX idx_company (company),
    INDEX idx_location (location)
);

INSERT INTO jobs (company, job_title, location, experience, skills, salary, description)
SELECT 'Google', 'AI/ML Engineer', 'Bangalore', '0-2 years', 'Python, Machine Learning, SQL', '10-15 LPA', 'AI and machine learning role requiring Python, SQL and machine learning.'
WHERE NOT EXISTS (
    SELECT 1 FROM jobs WHERE company='Google' AND job_title='AI/ML Engineer' AND location='Bangalore'
);
