import sys
import os
import time
import re
from typing import Optional
from collections import defaultdict
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.fast_api_app import app
from app.services.db_service import (
    init_db,
    create_case as db_create_case,
    update_case_status as db_update_case_status,
    get_case as db_get_case,
    list_cases as db_list_cases,
    seed_demo_data as db_seed_demo_data
)
from google.genai import types

# Simple in-memory rate limiting
RATE_LIMIT_WINDOW = 60  # 1 minute window
RATE_LIMIT_MAX_REQUESTS = 10  # max 10 requests per minute
request_history = defaultdict(list)

def is_rate_limited(ip: str) -> bool:
    now = time.time()
    # Remove timestamps older than window
    request_history[ip] = [t for t in request_history[ip] if now - t < RATE_LIMIT_WINDOW]
    if len(request_history[ip]) >= RATE_LIMIT_MAX_REQUESTS:
        return True
    request_history[ip].append(now)
    return False

# Initialize SQLite database
init_db()

@app.get("/health")
def health_endpoint():
    """Simple health endpoint returning status."""
    return {"status": "ok", "timestamp": time.time()}

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    """Sends report/chat to MajiGuardCoordinator agent."""
    # Rate limit check
    client_ip = request.client.host if request.client else "unknown"
    if is_rate_limited(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later."
        )

    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    user_id = data.get("user_id", "default_user")
    session_id = data.get("session_id")
    message_text = data.get("message", "").strip()

    if not message_text:
        raise HTTPException(status_code=400, detail="Message content cannot be empty")
        
    if len(message_text) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Message exceeds safety limit of 1000 characters."
        )

    runner = app.state.runner

    # Create new session if none exists
    if not session_id:
        session = await runner.session_service.create_session_async(
            user_id=user_id, app_name=app.state.agent_app_name
        )
        session_id = session.id

    message = types.Content(
        role="user", parts=[types.Part.from_text(text=message_text)]
    )

    response_text = ""
    try:
        # Run MajiGuardCoordinator
        async for event in runner.run_async(
            new_message=message,
            user_id=user_id,
            session_id=session_id,
        ):
            if event.content and event.content.parts:
                response_text += "".join(p.text for p in event.content.parts if p.text)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

    # Retrieve updated session state
    session_obj = await runner.session_service.get_session_async(session_id)
    questions_asked = session_obj.state.get("questions_asked", 0)
    
    # Detect if we have generated the final case report
    is_final = "Case ID:" in response_text or "MG-" in response_text

    case_details = None
    if is_final:
        # Try to parse the case ID from the response text
        case_id_match = re.search(r'MG-\d+-\w+|MG-DEMO-\d+', response_text)
        if case_id_match:
            case_id = case_id_match.group(0)
            case_details = db_get_case(case_id)

    return {
        "session_id": session_id,
        "response": response_text,
        "is_final": is_final,
        "questions_asked": questions_asked,
        "case_details": case_details
    }

@app.get("/api/cases")
def list_cases_endpoint(priority: Optional[str] = None, issue_type: Optional[str] = None):
    """Retrieve all triage cases, optionally filtered."""
    try:
        cases = db_list_cases(priority, issue_type)
        return cases
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database lookup failed: {str(e)}")

@app.get("/api/cases/{case_id}")
def get_case_endpoint(case_id: str):
    """Retrieve full details of a specific case."""
    case = db_get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@app.post("/api/cases/{case_id}/status")
async def update_status_endpoint(case_id: str, request: Request):
    """Updates status of a case."""
    try:
        data = await request.json()
        new_status = data.get("status")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    if new_status not in ["new", "reviewing", "assigned", "resolved"]:
        raise HTTPException(status_code=400, detail="Invalid status value")

    success = db_update_case_status(case_id, new_status)
    if not success:
        raise HTTPException(status_code=404, detail="Case not found or update failed")
    
    return {"status": "success", "case_id": case_id, "new_status": new_status}

@app.post("/api/demo/load")
def load_demo_endpoint():
    """Seeds SQLite database with the demo scenarios."""
    try:
        db_seed_demo_data()
        return {"status": "success", "message": "Demo cases loaded successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Seeding failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Start the server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
