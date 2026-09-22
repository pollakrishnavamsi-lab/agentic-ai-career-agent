import re
from pathlib import Path


# =========================================================
# SKILL ALIASES
# =========================================================

SKILL_ALIASES = {

    "ml": "Machine Learning",
    "machine learning": "Machine Learning",

    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",

    "gen ai": "Generative AI",
    "genai": "Generative AI",
    "generative ai": "Generative AI",

    "llm": "LLM",
    "llms": "LLM",
    "large language models": "LLM",

    "nlp": "NLP",
    "natural language processing": "NLP",

    "python": "Python",
    "sql": "SQL",
    "mysql": "MySQL",

    "pandas": "Pandas",
    "numpy": "NumPy",

    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "keras": "Keras",

    "scikit-learn": "Scikit-learn",
    "sklearn": "Scikit-learn",

    "flask": "Flask",
    "fastapi": "FastAPI",

    "docker": "Docker",
    "kubernetes": "Kubernetes",

    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",

    "rag": "RAG",
    "prompt engineering": "Prompt Engineering",

    "agentic ai": "Agentic AI",
    "ai agents": "AI Agents",

    "cnn": "CNN",
    "lstm": "LSTM",
    "deep learning": "Deep Learning",

    "computer vision": "Computer Vision",

    "git": "Git",
    "github": "GitHub",

    "data engineering": "Data Engineering",
    "data science": "Data Science",

    "power bi": "Power BI",
    "tableau": "Tableau",

    "spark": "Spark",

    "oracle cloud": "Oracle Cloud",

    "excel": "Excel",
    "microsoft excel": "Excel",

    "java": "Java",
    "c++": "C++",
    "javascript": "JavaScript",

    "html": "HTML",
    "css": "CSS",

    "mongodb": "MongoDB",
    "postgresql": "PostgreSQL",

    "rest api": "REST API",
    "api": "API",

    "langchain": "LangChain",
    "mcp": "MCP",
}


# =========================================================
# TEXT EXTRACTION
# =========================================================

def _extract_text(path: Path):

    ext = path.suffix.lower()

    if ext == ".pdf":

        from pypdf import PdfReader

        reader = PdfReader(str(path))

        parts = []

        for page in reader.pages:

            text = page.extract_text() or ""

            parts.append(text)

        return "\n".join(parts)


    if ext == ".docx":

        from docx import Document

        doc = Document(str(path))

        paragraphs = []

        for paragraph in doc.paragraphs:

            if paragraph.text.strip():

                paragraphs.append(paragraph.text.strip())

        return "\n".join(paragraphs)


    if ext == ".txt":

        return path.read_text(
            encoding="utf-8",
            errors="ignore"
        )


    raise ValueError("Unsupported file type")


# =========================================================
# CLEAN TEXT
# =========================================================

def _clean_text(text):

    text = text.replace("\r", "\n")

    # Remove excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()


# =========================================================
# SKILLS
# =========================================================

def _extract_skills(text):

    lower = text.lower()

    found = []

    for alias, canonical in SKILL_ALIASES.items():

        pattern = (
            r"(?<!\w)"
            + re.escape(alias)
            + r"(?!\w)"
        )

        if re.search(pattern, lower):

            if canonical not in found:

                found.append(canonical)

    return sorted(found)


# =========================================================
# EMAIL
# =========================================================

def _extract_email(text):

    match = re.search(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        text
    )

    if match:

        return match.group(0)

    return ""


# =========================================================
# PHONE
# =========================================================

def _extract_phone(text):

    patterns = [

        r"\+91[\s-]?\d{10}",

        r"\b\d{10}\b",

        r"\+?\d{1,3}[\s-]?\d{3,5}[\s-]?\d{4,6}",

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text
        )

        if match:

            return match.group(0)

    return ""


# =========================================================
# NAME
# =========================================================

def _extract_name(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:

        return ""


    # First few lines usually contain the candidate name.
    for line in lines[:8]:

        cleaned = line.strip()

        # Ignore obvious headings/contact lines
        if any(
            word in cleaned.lower()
            for word in [
                "resume",
                "curriculum vitae",
                "email",
                "phone",
                "mobile",
                "linkedin",
                "github",
                "@"
            ]
        ):

            continue


        # Candidate name usually has 2-4 words
        words = cleaned.split()

        if 2 <= len(words) <= 5:

            if all(
                re.match(
                    r"^[A-Za-z][A-Za-z.'-]*$",
                    word
                )
                for word in words
            ):

                return cleaned

    return ""


# =========================================================
# LOCATION
# =========================================================

def _extract_location(text):

    patterns = [

        r"(?:location|address|based in)\s*[:\-]\s*([^\n]+)",

        r"(?:Hyderabad|Bangalore|Bengaluru|Chennai|Mumbai|Delhi|Pune|Vijayawada|Kolkata|Kerala|Tamil Nadu|Telangana|Andhra Pradesh)[^\n]*",

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.I
        )

        if match:

            value = match.group(1) if match.lastindex else match.group(0)

            return value.strip(" :-")


    return ""


# =========================================================
# LINKEDIN
# =========================================================

def _extract_linkedin(text):

    match = re.search(
        r"(https?://(?:www\.)?linkedin\.com/[^\s]+)",
        text,
        flags=re.I
    )

    if match:

        return match.group(1).rstrip(".,)")

    return ""


# =========================================================
# GITHUB
# =========================================================

def _extract_github(text):

    match = re.search(
        r"(https?://(?:www\.)?github\.com/[^\s]+)",
        text,
        flags=re.I
    )

    if match:

        return match.group(1).rstrip(".,)")

    return ""


# =========================================================
# EDUCATION
# =========================================================

def _extract_education(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    education = []

    education_keywords = [

        "b.tech",
        "btech",
        "b.e",
        "be ",
        "bachelor",
        "m.tech",
        "mtech",
        "m.e",
        "master",
        "b.sc",
        "bsc",
        "m.sc",
        "msc",
        "phd",
        "computer science",
        "information technology",
        "engineering",

    ]


    for i, line in enumerate(lines):

        lower = line.lower()

        if any(
            keyword in lower
            for keyword in education_keywords
        ):

            block = [line]

            # Include next 1-2 lines if they look like
            # university/year/CGPA information.

            for next_line in lines[i + 1:i + 3]:

                next_lower = next_line.lower()

                if (
                    "university" in next_lower
                    or "college" in next_lower
                    or "institute" in next_lower
                    or "cgpa" in next_lower
                    or "gpa" in next_lower
                    or re.search(r"\b20\d{2}\b", next_line)
                ):

                    block.append(next_line)

            value = " | ".join(block)

            if value not in education:

                education.append(value)


    return education[:6]


# =========================================================
# EXPERIENCE
# =========================================================

def _extract_experience(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    experience = []

    experience_keywords = [

        "intern",
        "internship",
        "experience",
        "developer",
        "engineer",
        "analyst",
        "trainee",
        "software",
        "data scientist",
        "machine learning engineer",
        "ai engineer",

    ]


    for i, line in enumerate(lines):

        lower = line.lower()

        if any(
            keyword in lower
            for keyword in experience_keywords
        ):

            # Avoid treating the section heading itself as experience
            if lower.strip() in [
                "experience",
                "work experience",
                "professional experience",
                "internships",
            ]:

                continue

            block = [line]

            for next_line in lines[i + 1:i + 3]:

                if len(next_line) > 3:

                    block.append(next_line)

            value = " | ".join(block)

            if value not in experience:

                experience.append(value)


    return experience[:8]


# =========================================================
# EXPERIENCE YEARS
# =========================================================

def _extract_experience_mentions(text):

    patterns = [

        r"\b\d+(?:\.\d+)?\s*(?:\+|to|-)?\s*\d*\s*years?\b",

        r"\b\d+(?:\.\d+)?\s*months?\b",

    ]

    results = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
            flags=re.I
        )

        results.extend(matches)


    unique = []

    for item in results:

        item = item.strip()

        if item not in unique:

            unique.append(item)


    return unique[:8]


# =========================================================
# PROJECTS
# =========================================================

def _extract_projects(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    projects = []

    project_section = False

    for i, line in enumerate(lines):

        lower = line.lower()


        if re.match(
            r"^(projects?|academic projects?|personal projects?)$",
            lower
        ):

            project_section = True

            continue


        if project_section:

            # Stop at next major section
            if re.match(
                r"^(education|experience|skills|certifications?|achievements?|contact|summary|objective)$",
                lower
            ):

                project_section = False

                continue


            # Ignore extremely short lines
            if len(line) < 4:

                continue


            block = [line]

            for next_line in lines[i + 1:i + 4]:

                if len(next_line) > 10:

                    block.append(next_line)


            value = " | ".join(block)

            if value not in projects:

                projects.append(value)


    return projects[:8]


# =========================================================
# CERTIFICATIONS
# =========================================================

def _extract_certifications(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    certifications = []

    certification_section = False

    for i, line in enumerate(lines):

        lower = line.lower()


        if re.match(
            r"^(certifications?|certificates?)$",
            lower
        ):

            certification_section = True

            continue


        if certification_section:

            if re.match(
                r"^(education|experience|projects?|skills|achievements?|summary|objective)$",
                lower
            ):

                certification_section = False

                continue


            if len(line) < 4:

                continue


            certifications.append(line)


    # Also detect common certification phrases
    for line in lines:

        lower = line.lower()

        if (
            "certified" in lower
            or "certification" in lower
            or "oracle certified" in lower
        ):

            if line not in certifications:

                certifications.append(line)


    return list(dict.fromkeys(certifications))[:8]


# =========================================================
# SUMMARY
# =========================================================

def _extract_summary(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    summary = []

    summary_started = False

    for i, line in enumerate(lines):

        lower = line.lower()


        if re.match(
            r"^(summary|professional summary|profile|objective|career objective)$",
            lower
        ):

            summary_started = True

            continue


        if summary_started:

            if re.match(
                r"^(education|experience|projects?|skills|certifications?|achievements?|technical skills)$",
                lower
            ):

                break


            summary.append(line)


    if summary:

        return " ".join(summary)[:1000]


    return ""


# =========================================================
# SECTION STATISTICS
# =========================================================

def _calculate_profile_strength(profile):

    score = 0

    if profile.get("name"):
        score += 10

    if profile.get("email"):
        score += 10

    if profile.get("education"):
        score += 15

    if profile.get("skills"):
        score += 20

    if profile.get("projects"):
        score += 15

    if profile.get("experience"):
        score += 15

    if profile.get("certifications"):
        score += 10

    if profile.get("summary"):
        score += 5

    return min(score, 100)


# =========================================================
# MAIN RESUME FUNCTION
# =========================================================

def extract_resume(path):

    path = Path(path)

    text = _extract_text(path)

    text = _clean_text(text)


    if not text.strip():

        raise ValueError(
            "No text could be extracted. "
            "This may be a scanned/image-only document; "
            "OCR is required."
        )


    # Extract all sections
    skills = _extract_skills(text)

    education = _extract_education(text)

    experience = _extract_experience(text)

    experience_mentions = _extract_experience_mentions(text)

    projects = _extract_projects(text)

    certifications = _extract_certifications(text)

    summary = _extract_summary(text)


    profile = {

        "name": _extract_name(text),

        "email": _extract_email(text),

        "phone": _extract_phone(text),

        "location": _extract_location(text),

        "linkedin": _extract_linkedin(text),

        "github": _extract_github(text),

        "summary": summary,

        "skills": skills,

        "education": education,

        "experience": experience,

        "experience_mentions": experience_mentions,

        "projects": projects,

        "certifications": certifications,

        "skill_count": len(skills),

        "profile_strength": 0,

        "raw_text": text[:30000],

    }


    profile["profile_strength"] = _calculate_profile_strength(
        profile
    )


    return profile