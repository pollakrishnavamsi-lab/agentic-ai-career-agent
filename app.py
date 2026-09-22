import os
import traceback
from pathlib import Path

from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from resume_parser import extract_resume
from matcher import rank_jobs
from agent import CareerAgent


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "change-this-secret"
)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {
    "pdf",
    "docx",
    "txt"
}


# ============================================================
# CAREER AGENT
# ============================================================

career_agent = CareerAgent()


# ============================================================
# HELPERS
# ============================================================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ============================================================
# HOME
# ============================================================

@app.get("/")
def index():

    return render_template("index.html")


# ============================================================
# RESUME UPLOAD
# ============================================================

@app.post("/api/upload")
def upload_resume():

    try:

        if "resume" not in request.files:

            return jsonify({
                "error": "No resume file was uploaded."
            }), 400

        file = request.files["resume"]

        if not file.filename:

            return jsonify({
                "error": "Please choose a resume."
            }), 400

        if not allowed_file(file.filename):

            return jsonify({
                "error": "Supported formats: PDF, DOCX, TXT."
            }), 400

        filename = secure_filename(
            file.filename
        )

        path = UPLOAD_DIR / filename

        file.save(path)

        print("\n========================================")
        print("RESUME UPLOAD")
        print("========================================")
        print("File:", filename)
        print("Path:", path)
        print("========================================\n")

        profile = extract_resume(path)

        if not profile:

            return jsonify({
                "error":
                "Could not extract information from the resume."
            }), 500

        # Don't store raw resume text inside Flask session
        session_profile = dict(profile)

        session_profile.pop(
            "raw_text",
            None
        )

        session["profile"] = session_profile

        session["resume_name"] = filename

        session["chat_history"] = []

        session.modified = True

        recommendations = rank_jobs(profile)

        print("\n========================================")
        print("RESUME ANALYSIS SUCCESS")
        print("========================================")

        print(
            "Skills found:",
            len(profile.get("skills", []))
        )

        print(
            "Jobs ranked:",
            len(recommendations)
        )

        print("========================================\n")

        return jsonify({

            "message":
                f"I've analyzed {filename}. "
                f"I found "
                f"{len(profile.get('skills', []))} skills "
                f"and ranked your best job matches.",

            "resume_name": filename,

            "profile": profile,

            "recommendations": recommendations

        }), 200

    except Exception as exc:

        print("\n========================================")
        print("RESUME PROCESSING ERROR")
        print("========================================")

        traceback.print_exc()

        print("========================================\n")

        return jsonify({
            "error":
                f"Resume processing failed: {str(exc)}"
        }), 500


# ============================================================
# CAREER AGENT CHAT
# ============================================================

@app.post("/api/chat")
def chat():

    print("\n========================================")
    print("CAREER AGENT REQUEST")
    print("========================================")

    try:

        payload = request.get_json(
            silent=True
        ) or {}

        message = (
            payload.get("message") or ""
        ).strip()

        print(
            "User message:",
            message
        )

        if not message:

            return jsonify({
                "error": "Message is required."
            }), 400

        profile = session.get(
            "profile"
        )

        if not profile:

            return jsonify({

                "reply":
                    "Please upload your resume first. "
                    "Then I can act as your career agent.",

                "used_tools": []

            }), 200

        history = session.get(
            "chat_history",
            []
        )

        if not isinstance(history, list):

            history = []

        history = history[-8:]

        print(
            "Profile found."
        )

        print(
            "Calling NEW CareerAgent..."
        )

        # ====================================================
        # ACTUAL AGENT
        # ====================================================

        result = career_agent.chat(
            message,
            profile,
            history
        )

        print(
            "CareerAgent completed."
        )

        print(
            "Tools used:",
            result.get("used_tools", [])
        )

        reply = result.get(
            "reply",
            "I couldn't generate a response."
        )

        used_tools = result.get(
            "used_tools",
            []
        )

        # ====================================================
        # CHAT HISTORY
        # ====================================================

        history.append({

            "role": "user",

            "content": message

        })

        history.append({

            "role": "assistant",

            "content": reply

        })

        session["chat_history"] = history[-12:]

        session.modified = True

        print("\n========================================")
        print("CAREER AGENT SUCCESS")
        print("========================================")

        print(
            "Tools:",
            used_tools
        )

        print("========================================\n")

        return jsonify({

            "reply": reply,

            "used_tools": used_tools

        }), 200

    except Exception as exc:

        # IMPORTANT:
        # Do NOT silently fall back to the old agent.
        # Show the real error so we can fix it.

        print("\n========================================")
        print("ACTUAL CAREER AGENT ERROR")
        print("========================================")

        traceback.print_exc()

        print("========================================\n")

        return jsonify({

            "error":
                "Career Agent error: "
                + str(exc)

        }), 500


# ============================================================
# PROFILE
# ============================================================

@app.get("/api/profile")
def get_profile():

    return jsonify({

        "profile":
            session.get("profile"),

        "resume_name":
            session.get("resume_name")

    }), 200


# ============================================================
# RESET
# ============================================================

@app.post("/api/reset")
def reset():

    session.clear()

    return jsonify({

        "message":
            "Session reset successfully."

    })


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(413)
def file_too_large(error):

    return jsonify({

        "error":
            "File is too large. Maximum allowed size is 10 MB."

    }), 413


@app.errorhandler(404)
def not_found(error):

    return jsonify({

        "error":
            "API endpoint not found."

    }), 404


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    print("\n========================================")
    print("            AI JOB AGENT")
    print("========================================")

    print(
        "Server:",
        "http://127.0.0.1:5000"
    )

    print(
        "Model:",
        os.getenv(
            "OPENAI_MODEL",
            "gpt-5.6-luna"
        )
    )

    print(
        "OpenAI Key:",
        "Configured"
        if os.getenv("OPENAI_API_KEY")
        else "NOT CONFIGURED"
    )

    print("========================================\n")

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )