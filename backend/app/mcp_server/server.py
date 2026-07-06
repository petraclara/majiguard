import sys
import os
import json
from typing import Optional, Dict, Any

# Ensure backend directory is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MajiGuard MCP Server")

@mcp.tool()
def search_guidance(query: str) -> str:
    """Search the local water-support knowledge base for safe, practical guidance.
    
    Args:
        query: The search terms or issue description to lookup.
        
    Returns:
        JSON string containing matching articles with titles and guidance.
    """
    from app.services.kb_service import search_kb
    results = search_kb(query)
    return json.dumps(results)

@mcp.tool()
def create_case(case_data: dict) -> str:
    """Save a structured water-access case in SQLite and return a case ID.
    
    Args:
        case_data: Dictionary containing case fields:
                   original_report (str), redacted_report (str),
                   follow_up_answers (dict), issue_type (str), priority (str),
                   affected_group (str), duration (str), location_hint (str),
                   assessment_summary (str), immediate_guidance (str),
                   recommended_actions (str).
                   
    Returns:
        The generated case ID (e.g. MG-YYYYMMDD-XXXX).
    """
    from app.services.db_service import create_case as db_create_case
    case_id = db_create_case(case_data)
    return case_id

@mcp.tool()
def update_case_status(case_id: str, status: str) -> str:
    """Updates the status of a case.
    
    Args:
        case_id: The ID of the case (e.g. MG-20260705-1234).
        status: The new status. Must be one of: new, reviewing, assigned, resolved.
        
    Returns:
        Status string 'success' or 'failed'.
    """
    from app.services.db_service import update_case_status as db_update_case_status
    try:
        success = db_update_case_status(case_id, status)
        return "success" if success else "failed"
    except Exception as e:
        return f"error: {str(e)}"

@mcp.tool()
def list_cases(priority: Optional[str] = None, issue_type: Optional[str] = None) -> str:
    """List cases in the database, optionally filtered by priority and issue type.
    
    Args:
        priority: Optional priority filter (Low, Medium, High, Critical).
        issue_type: Optional issue type filter (possible_contamination, infrastructure_failure, water_shortage, long_queue_or_access_issue, other).
        
    Returns:
        JSON string containing list of matching cases.
    """
    from app.services.db_service import list_cases as db_list_cases
    cases = db_list_cases(priority, issue_type)
    return json.dumps(cases)

@mcp.tool()
def get_case(case_id: str) -> str:
    """Retrieve full details of a specific case by its ID.
    
    Args:
        case_id: The unique case ID.
        
    Returns:
        JSON string of the case, or 'null' if not found.
    """
    from app.services.db_service import get_case as db_get_case
    case = db_get_case(case_id)
    return json.dumps(case) if case else "null"

if __name__ == "__main__":
    mcp.run()
