# AI Job Agent v2

A Flask + MySQL + LLM agentic job recommendation application with PDF/DOCX/TXT resume ingestion, hybrid matching, conversational agent tools, and a modern dashboard UI.

## Architecture

Resume -> Flask POST /api/upload -> parser -> candidate profile -> MySQL jobs + semantic retrieval -> ranked jobs -> UI/chat.

The chat agent can call two local tools:
- `search_jobs`
- `rank_candidate_jobs`

RAG-style retrieval is implemented in `matcher.py`: the system retrieves/ranks job descriptions using semantic similarity when `sentence-transformers` is available and falls back to lexical similarity if it is not.

## Setup

1. Create a virtual environment.
2. Install requirements: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill values.
4. Run `schema.sql` in MySQL Workbench.
5. If you have Adzuna credentials, run `python job_scraper.py` to populate jobs.
6. Start: `python app.py`
7. Open http://127.0.0.1:5000

## Important

Never commit `.env`. Do not hardcode database passwords or API keys.

If `OPENAI_API_KEY` is missing, the application still runs using a deterministic local career-agent fallback. Add the key to activate the LLM tool-calling agent.
