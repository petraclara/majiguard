from app.services.priority_service import evaluate_priority_rules

def test_priority_contamination_vulnerable():
    # Contamination affecting children/school -> Critical
    intake_data = {
        "issue_type": "possible_contamination",
        "affected_group": "school children",
        "safety_concerns": "children are drinking from it"
    }
    priority, reasoning = evaluate_priority_rules(intake_data)
    assert priority == "Critical"
    assert "vulnerable groups" in reasoning

def test_priority_contamination_general():
    # General contamination -> High
    intake_data = {
        "issue_type": "possible_contamination",
        "affected_group": "local villagers",
        "safety_concerns": "water smells like gasoline"
    }
    priority, _ = evaluate_priority_rules(intake_data)
    assert priority == "High"

def test_priority_water_shortage_no_alternative():
    # Water shortage for multiple days, no alternative -> High
    intake_data = {
        "issue_type": "water_shortage",
        "duration": "three days",
        "alternative_water": "none"
    }
    priority, _ = evaluate_priority_rules(intake_data)
    assert priority == "High"

def test_priority_infrastructure_with_alternative():
    # Broken water point, alternative available -> Medium
    intake_data = {
        "issue_type": "infrastructure_failure",
        "alternative_water": "we can use the old well"
    }
    priority, _ = evaluate_priority_rules(intake_data)
    assert priority == "Medium"

def test_priority_long_queue_no_risk():
    # Long queue without safety risk -> Low
    intake_data = {
        "issue_type": "long_queue_or_access_issue",
        "safety_concerns": "none"
    }
    priority, _ = evaluate_priority_rules(intake_data)
    assert priority == "Low"

def test_priority_long_queue_with_risk():
    # Long queue with safety risk (fights) -> Medium
    intake_data = {
        "issue_type": "long_queue_or_access_issue",
        "safety_concerns": "people are fighting in the queue"
    }
    priority, _ = evaluate_priority_rules(intake_data)
    assert priority == "Medium"
