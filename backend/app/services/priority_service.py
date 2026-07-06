from typing import Dict, Any, Tuple

def evaluate_priority_rules(intake_data: Dict[str, Any]) -> Tuple[str, str]:
    """Applies transparent rules to determine case priority and reasoning.
    
    Args:
        intake_data: Dictionary containing location_hint, issue_type, affected_group,
                     duration, safety_concerns, alternative_water.
                     
    Returns:
        A tuple of (priority, reasoning_summary).
    """
    issue_type = intake_data.get("issue_type", "other")
    safety_concerns = (intake_data.get("safety_concerns") or "").lower()
    affected_group = (intake_data.get("affected_group") or "").lower()
    duration = (intake_data.get("duration") or "").lower()
    alternative_water = (intake_data.get("alternative_water") or "").lower()

    # Rule 1: Possible contamination affecting children, schools, clinics, or many people: High or Critical
    if issue_type == "possible_contamination":
        vulnerable_keywords = ["school", "child", "clinic", "hospital", "student", "kid", "baby", "nursery", "health", "many"]
        is_vulnerable = any(k in affected_group or k in safety_concerns for k in vulnerable_keywords)
        if is_vulnerable:
            return "Critical", "Possible contamination directly affecting vulnerable groups (children, schools, clinics) or a large group."
        return "High", "Possible contamination reported, posing health risks to the community."

    # Rule 2: No water for multiple days with no alternative source: High
    if issue_type == "water_shortage" or "no water" in safety_concerns:
        # Check if duration indicates multiple days
        is_multi_day = any(d in duration for d in ["day", "week", "month"])
        # Check if alternative water is available
        no_alternative = not alternative_water or any(a in alternative_water for a in ["no", "none", "nothing", "don't have", "zero"])
        
        if is_multi_day and no_alternative:
            return "High", "Water shortage lasting multiple days with no alternative water source reported."

    # Rule 3: Broken water point with alternative sources available: Medium
    if issue_type == "infrastructure_failure":
        return "Medium", "Infrastructure failure (broken pump/well) but alternative water source is available."

    # Rule 4: Long queues without safety risk: Low or Medium
    if issue_type == "long_queue_or_access_issue":
        safety_risk_keywords = ["unsafe", "fight", "conflict", "threat", "danger", "security", "dark", "night"]
        has_safety_risk = any(k in safety_concerns or k in affected_group for k in safety_risk_keywords)
        if has_safety_risk:
            return "Medium", "Long queue at water collection point with reported safety or security concerns."
        return "Low", "Long queue or access delay at water point without immediate safety or security risks."

    return "Low", "General water-access report or question with low risk of health or safety impact."
