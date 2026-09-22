import json
import os
import traceback

from dotenv import load_dotenv
from openai import OpenAI

from db import search_jobs
from matcher import rank_jobs
from rag import retrieve, format_context


load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY)


class CareerAgent:

    def __init__(self):
        self.client = client
        self.model = MODEL

    # =========================================================
    # TOOL 1: SEARCH JOBS
    # =========================================================

    def search_jobs_tool(self, query):
        try:
            jobs = search_jobs(query)

            return {
                "success": True,
                "jobs": jobs[:10]
            }

        except Exception as exc:
            traceback.print_exc()

            return {
                "success": False,
                "error": str(exc)
            }

    # =========================================================
    # TOOL 2: RANK JOBS FOR CANDIDATE
    # =========================================================

    def rank_candidate_jobs_tool(self, profile):
        try:
            jobs = rank_jobs(profile, 5)

            return {
                "success": True,
                "recommendations": jobs
            }

        except Exception as exc:
            traceback.print_exc()

            return {
                "success": False,
                "error": str(exc)
            }

    # =========================================================
    # TOOL 3: RAG KNOWLEDGE RETRIEVAL
    # =========================================================

    def retrieve_knowledge_tool(self, query):
        try:
            results = retrieve(query, top_k=4)

            context = format_context(results)

            return {
                "success": True,
                "query": query,
                "results": results,
                "context": context
            }

        except Exception as exc:
            traceback.print_exc()

            return {
                "success": False,
                "error": str(exc)
            }

    # =========================================================
    # OPENAI TOOL DEFINITIONS
    # =========================================================

    def get_tools(self):

        return [

            {
                "type": "function",
                "name": "search_jobs",
                "description": (
                    "Search the MySQL job database for jobs matching "
                    "a keyword, skill, company, location or job title."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": (
                                "Job search query such as "
                                "'AI ML jobs', 'Python jobs', "
                                "'Bangalore data scientist'"
                            )
                        }
                    },
                    "required": ["query"]
                }
            },

            {
                "type": "function",
                "name": "rank_candidate_jobs",
                "description": (
                    "Rank jobs according to the candidate's resume profile "
                    "and identify the strongest job matches."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },

            {
                "type": "function",
                "name": "retrieve_knowledge",
                "description": (
                    "Retrieve relevant information from the career and "
                    "AI/ML knowledge base using semantic search. "
                    "Use this when the user asks conceptual questions "
                    "about AI, ML, GenAI, RAG, agents, Python, SQL, "
                    "interviews, career preparation or related topics."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": (
                                "The knowledge question to search for."
                            )
                        }
                    },
                    "required": ["query"]
                }
            }

        ]

    # =========================================================
    # SYSTEM PROMPT
    # =========================================================

    def system_prompt(self, profile):

        skills = profile.get("skills", [])

        education = profile.get(
            "education",
            "Not available"
        )

        experience = profile.get(
            "experience",
            "Not available"
        )

        return f"""
You are an intelligent AI Career Agent.

Your job is to help the candidate with:
- Job recommendations
- Job searching
- Skill-gap analysis
- AI/ML career guidance
- GenAI guidance
- Interview preparation
- Learning roadmaps
- Resume-related career advice

You have access to three tools:

1. search_jobs
Use this when the user wants to search for jobs.

2. rank_candidate_jobs
Use this when the user asks for their best matching jobs,
job recommendations, or skill gaps based on their resume.

3. retrieve_knowledge
Use this when the user asks conceptual or educational questions
about AI, ML, GenAI, RAG, Agentic AI, Python, SQL, interviews,
career preparation or related topics.

IMPORTANT:
You should decide which tool is appropriate based on the user's
question.

You may use more than one tool when necessary.

For example:
- "What is RAG?" → retrieve_knowledge
- "Explain CNN" → retrieve_knowledge
- "How should I prepare for an AI interview?" → retrieve_knowledge
- "Find Python jobs" → search_jobs
- "What are my best jobs?" → rank_candidate_jobs
- "What skills am I missing for ML jobs?" → rank_candidate_jobs
- "Find AI jobs in Bangalore and tell me what skills I need" →
  search_jobs + retrieve_knowledge

After receiving tool results, provide a clear and useful answer.

Do not mention internal tool names unless useful for explaining
the architecture.

Candidate profile:

Skills:
{skills}

Education:
{education}

Experience:
{experience}
"""

    # =========================================================
    # TOOL EXECUTION
    # =========================================================

    def execute_tool(self, tool_name, arguments, profile):

        print("\n----------------------------------------")
        print("AGENT TOOL:", tool_name)
        print("ARGUMENTS:", arguments)
        print("----------------------------------------")

        if tool_name == "search_jobs":

            query = arguments.get("query", "")

            return self.search_jobs_tool(query)

        elif tool_name == "rank_candidate_jobs":

            return self.rank_candidate_jobs_tool(profile)

        elif tool_name == "retrieve_knowledge":

            query = arguments.get("query", "")

            return self.retrieve_knowledge_tool(query)

        return {
            "success": False,
            "error": f"Unknown tool: {tool_name}"
        }

    # =========================================================
    # MAIN AGENT
    # =========================================================

    def chat(self, message, profile, history=None):

        if history is None:
            history = []

        instructions = self.system_prompt(profile)

        conversation = []

        # Keep recent conversation
        for item in history[-8:]:

            if not isinstance(item, dict):
                continue

            role = item.get("role")
            content = item.get("content")

            if role in ["user", "assistant"] and content:
                conversation.append({
                    "role": role,
                    "content": content
                })

        conversation.append({
            "role": "user",
            "content": message
        })

        tools = self.get_tools()

        used_tools = []

        try:

            print("\n========================================")
            print("CAREER AGENT START")
            print("========================================")

            response = self.client.responses.create(
                model=self.model,
                instructions=instructions,
                input=conversation,
                tools=tools
            )

            # Agent loop
            for iteration in range(5):

                print(
                    f"\nAgent iteration: {iteration + 1}"
                )

                function_calls = []

                for item in response.output:

                    if getattr(item, "type", None) == "function_call":
                        function_calls.append(item)

                # No tool call = final answer
                if not function_calls:

                    final_answer = response.output_text

                    print("\nFINAL ANSWER GENERATED")
                    print("Tools used:", used_tools)
                    print("========================================\n")

                    return {
                        "reply": final_answer,
                        "used_tools": used_tools
                    }

                # Execute requested tools
                tool_outputs = []

                for call in function_calls:

                    try:
                        arguments = json.loads(
                            call.arguments
                        )
                    except Exception:
                        arguments = {}

                    result = self.execute_tool(
                        call.name,
                        arguments,
                        profile
                    )

                    used_tools.append(call.name)

                    tool_outputs.append({
                        "type": "function_call_output",
                        "call_id": call.call_id,
                        "output": json.dumps(
                            result,
                            default=str
                        )
                    })

                # Continue agent reasoning
                response = self.client.responses.create(
                    model=self.model,
                    instructions=instructions,
                    previous_response_id=response.id,
                    input=tool_outputs,
                    tools=tools
                )

            return {
                "reply": (
                    "I reached the maximum number of reasoning steps "
                    "while processing your request. Please try asking "
                    "the question in a simpler way."
                ),
                "used_tools": used_tools
            }

        except Exception as exc:

            print("\n========================================")
            print("CAREER AGENT ERROR")
            print("========================================")

            traceback.print_exc()

            print("========================================\n")

            raise exc