import json

from mcp.server import MCPServer

from db import search_jobs
from matcher import rank_jobs
from rag import retrieve, format_context


# =========================================================
# MCP SERVER
# =========================================================

mcp = MCPServer(
    "AI Career Agent MCP",
    instructions=(
        "MCP tools for the AI Career Agent. "
        "These tools provide job search, resume-job matching, "
        "and career knowledge retrieval."
    )
)


# =========================================================
# TOOL 1 — SEARCH JOBS
# =========================================================

@mcp.tool(
    name="search_jobs",
    title="Search Jobs",
    description=(
        "Search the job database for jobs matching a keyword, "
        "technology, company, role, location, or skill."
    )
)
def mcp_search_jobs(query: str) -> list:
    """
    Search jobs stored in MySQL.
    """

    print(f"\n[MCP] search_jobs -> {query}")

    jobs = search_jobs(query)

    print(f"[MCP] search_jobs returned {len(jobs)} jobs")

    return jobs


# =========================================================
# TOOL 2 — RESUME JOB MATCHING
# =========================================================

@mcp.tool(
    name="rank_candidate_jobs",
    title="Rank Candidate Jobs",
    description=(
        "Compare a candidate profile against available jobs "
        "and return the best matching jobs using the project's "
        "hybrid skill and semantic matching system."
    )
)
def mcp_rank_candidate_jobs(profile: dict) -> list:
    """
    Rank jobs against candidate profile.
    """

    print("\n[MCP] rank_candidate_jobs")

    results = rank_jobs(profile)

    print(
        f"[MCP] rank_candidate_jobs returned "
        f"{len(results)} recommendations"
    )

    return results


# =========================================================
# TOOL 3 — RAG KNOWLEDGE RETRIEVAL
# =========================================================

@mcp.tool(
    name="retrieve_knowledge",
    title="Retrieve Career Knowledge",
    description=(
        "Retrieve relevant information from the Career Agent "
        "knowledge base using semantic vector search. "
        "Use this for AI, ML, GenAI, RAG, agents, MCP, "
        "Python, SQL, interviews, and career preparation."
    )
)
def mcp_retrieve_knowledge(
    query: str,
    top_k: int = 4
) -> str:
    """
    Retrieve relevant RAG knowledge.
    """

    print(f"\n[MCP] retrieve_knowledge -> {query}")

    results = retrieve(
        query,
        top_k=top_k
    )

    context = format_context(results)

    print(
        f"[MCP] retrieve_knowledge returned "
        f"{len(results)} chunks"
    )

    return context


# =========================================================
# SERVER START
# =========================================================

if __name__ == "__main__":

    print("=" * 50)
    print("AI CAREER AGENT MCP SERVER")
    print("=" * 50)

    print("Available MCP tools:")
    print("1. search_jobs")
    print("2. rank_candidate_jobs")
    print("3. retrieve_knowledge")

    print("=" * 50)

    mcp.run(transport="stdio")