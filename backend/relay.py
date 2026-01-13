import os
import httpx
from dotenv import load_dotenv

load_dotenv()

RELAY_WEBHOOK_URL = os.getenv("RELAY_WEBHOOK_URL")

def send_issue_report(payload: dict):
    if not RELAY_WEBHOOK_URL:
        raise ValueError("Relay webhook URL not set")
    response = httpx.post(RELAY_WEBHOOK_URL, json=payload)
    response.raise_for_status()
    return response.json()
