# 🤖 Agentic AI Career Agent

An AI-powered career assistant that analyzes resumes, matches candidates with relevant jobs, and provides career and interview guidance through a conversational interface.

## 🚀 What the Project Does

The Career Agent combines resume parsing, job matching, semantic retrieval, and an AI agent to help users understand their job opportunities.

### Main Features

- 📄 Resume upload and parsing
- 🔎 Job matching based on resume skills
- 🤖 Conversational AI career assistant
- 🧠 RAG-style semantic retrieval
- 💼 Job search and ranking
- 🎯 Interview and career guidance
- 🔌 MCP-based tool integration
- 🗄️ MySQL database for job data
- 🌐 Flask-based web interface

## 🏗️ Architecture

```text
User
 │
 ▼
Web Interface
 │
 ├── Resume Upload
 │       │
 │       ▼
 │   Resume Parser
 │       │
 │       ▼
 │   Candidate Profile
 │
 └── Career Chat
         │
         ▼
    AI Career Agent
         │
    ┌────┴───────────────┐
    ▼                    ▼
Job Search Tool     Job Ranking Tool
    │                    │
    └─────────┬──────────┘
              ▼
        MySQL Job Data
              │
              ▼
     Semantic / RAG Retrieval
              │
              ▼
       Career Recommendations