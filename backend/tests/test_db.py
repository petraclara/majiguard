import os
import pytest
from app.services.db_service import (
    init_db,
    create_case,
    get_case,
    update_case_status,
    list_cases
)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    # Make sure database is initialized
    init_db()
    yield

def test_case_creation_and_retrieval():
    case_data = {
        "original_report": "The well is dry.",
        "redacted_report": "The well is dry.",
        "follow_up_answers": {"q1": "yes"},
        "issue_type": "water_shortage",
        "priority": "Medium",
        "affected_group": "Entire village",
        "duration": "1 week",
        "location_hint": "Center village",
        "assessment_summary": "Dry well reported.",
        "immediate_guidance": "Boil alternative water.",
        "recommended_actions": "Check well water levels.",
        "status": "new"
    }
    
    case_id = create_case(case_data)
    assert case_id is not None
    assert case_id.startswith("MG-")
    
    case = get_case(case_id)
    assert case is not None
    assert case["case_id"] == case_id
    assert case["original_report"] == "The well is dry."
    assert case["issue_type"] == "water_shortage"
    assert case["priority"] == "Medium"
    assert case["status"] == "new"

def test_case_status_updates():
    case_data = {
        "original_report": "Leak in the pipe.",
        "redacted_report": "Leak in the pipe.",
        "issue_type": "infrastructure_failure",
        "priority": "Low",
        "assessment_summary": "Pipe leak.",
        "immediate_guidance": "None",
        "recommended_actions": "Call plumber"
    }
    case_id = create_case(case_data)
    
    # Update status
    updated = update_case_status(case_id, "reviewing")
    assert updated is True
    
    case = get_case(case_id)
    assert case["status"] == "reviewing"
    
    # Try invalid status
    with pytest.raises(ValueError):
        update_case_status(case_id, "invalid_status")

def test_list_and_filter_cases():
    # Insert multiple cases to guarantee results
    create_case({
        "original_report": "Filtered case 1",
        "redacted_report": "Filtered case 1",
        "issue_type": "possible_contamination",
        "priority": "Critical",
        "assessment_summary": "High risk",
        "immediate_guidance": "None",
        "recommended_actions": "None"
    })
    
    create_case({
        "original_report": "Filtered case 2",
        "redacted_report": "Filtered case 2",
        "issue_type": "water_shortage",
        "priority": "Low",
        "assessment_summary": "Low risk",
        "immediate_guidance": "None",
        "recommended_actions": "None"
    })
    
    # List all
    all_cases = list_cases()
    assert len(all_cases) >= 2
    
    # Filter by priority
    critical_cases = list_cases(priority="Critical")
    assert len(critical_cases) >= 1
    assert all(c["priority"] == "Critical" for c in critical_cases)
    
    # Filter by issue_type
    shortage_cases = list_cases(issue_type="water_shortage")
    assert len(shortage_cases) >= 1
    assert all(c["issue_type"] == "water_shortage" for c in shortage_cases)
