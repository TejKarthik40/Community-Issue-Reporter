import re
def is_valid_phone(phone):
    # Accepts 10 digits, optional +country code
    pattern = r"^(\+\d{1,3}[- ]?)?\d{10}$"
    return re.match(pattern, phone)
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str


from dotenv import load_dotenv
import os
from supabase_helpers import insert_issue
from relay import send_issue_report

load_dotenv()

DEPT_EMAILS = {
    "road": os.getenv("ROAD_DEPT_EMAIL"),
    "streetlight": os.getenv("ELECTRICAL_DEPT_EMAIL"),
    "waste": os.getenv("SANITATION_DEPT_EMAIL"),
}

class ChatResponse(BaseModel):
    reply: str
    options: list = []


# In-memory session store (for demo)
user_sessions = {}

REQUIRED_FIELDS = ["reporter_name", "phone_number", "location", "description"]

def classify_issue(message):
    msg = message.lower()
    if any(w in msg for w in ["pothole", "road"]):
        return "road"
    if any(w in msg for w in ["light", "streetlight"]):
        return "streetlight"
    if any(w in msg for w in ["garbage", "waste"]):
        return "waste"
    return None

def get_missing_field(data):
    for field in REQUIRED_FIELDS:
        if not data.get(field):
            return field
    return None

def field_prompt(field):
    prompts = {
        "reporter_name": "May I have your name, please?",
        "phone_number": "May I have your phone number, please?",
        "location": "Please tell me the exact location of the issue.",
        "description": "Could you describe the issue in a few words?"
    }
    return prompts[field]

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # For demo, use a single session (no user auth)
    session = user_sessions.setdefault("default", {})
    msg = request.message.strip()

    # If no issue_type, ask for category
    if not session.get("issue_type"):
        # Try to classify from message
        issue_type = classify_issue(msg)
        if issue_type:
            session["issue_type"] = issue_type
        else:
            options = ["Road / Municipal Works", "Electrical (Streetlights)", "Sanitation (Waste & Garbage)"]
            session["pending_category"] = True
            return {"reply": "Which department does your issue relate to?", "options": options}

    # Handle category selection
    if session.get("pending_category"):
        if "road" in msg.lower():
            session["issue_type"] = "road"
        elif "electrical" in msg.lower() or "light" in msg.lower():
            session["issue_type"] = "streetlight"
        elif "sanitation" in msg.lower() or "waste" in msg.lower() or "garbage" in msg.lower():
            session["issue_type"] = "waste"
        else:
            return {"reply": "Please select a department:", "options": ["Road / Municipal Works", "Electrical (Streetlights)", "Sanitation (Waste & Garbage)"]}
        session.pop("pending_category")


    # Step-by-step: Only ask for one missing field at a time
    for field in REQUIRED_FIELDS:
        if not session.get(field):
            # If this is the first time asking, prompt for the field
            if session.get("awaiting_field") != field:
                session["awaiting_field"] = field
                return {"reply": field_prompt(field), "options": []}
            # If already awaiting this field, accept the user's message as the value
            if field == "phone_number":
                if not is_valid_phone(msg):
                    return {"reply": "Please enter a valid phone number (10 digits, optional country code).", "options": []}
            session[field] = msg
            session.pop("awaiting_field", None)
            # After accepting, check if more fields are missing (will prompt next on next message)
            break

    # Only proceed if all required fields are present
    missing = [f for f in REQUIRED_FIELDS if not session.get(f)]
    if missing:
        # Prompt for the next missing field
        next_field = missing[0]
        session["awaiting_field"] = next_field
        return {"reply": field_prompt(next_field), "options": []}

    issue_type = session["issue_type"]
    location = session["location"]
    description = session["description"]
    reporter_name = session["reporter_name"]
    phone_number = session["phone_number"]

    # Store in Supabase
    insert_issue(issue_type, location, description, reporter_name, phone_number)

    # Send to department via Relay webhook
    to_email = DEPT_EMAILS.get(issue_type)
    payload = {
        "to_email": to_email,
        "issue_type": issue_type,
        "location": location,
        "description": description,
        "reporter_name": reporter_name,
        "phone_number": phone_number
    }
    send_issue_report(payload)

    # Reset session
    user_sessions["default"] = {}

    return {"reply": f"Thank you, {reporter_name}. Your issue has been reported to the {issue_type} department.", "options": []}
