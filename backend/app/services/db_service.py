import os
import sqlite3
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "majiguard.db"
)

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            case_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            original_report TEXT NOT NULL,
            redacted_report TEXT NOT NULL,
            follow_up_answers TEXT NOT NULL, -- JSON string
            issue_type TEXT NOT NULL,
            priority TEXT NOT NULL,
            affected_group TEXT,
            duration TEXT,
            location_hint TEXT,
            assessment_summary TEXT NOT NULL,
            immediate_guidance TEXT NOT NULL,
            recommended_actions TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'new'
        )
    """)
    conn.commit()
    conn.close()

def create_case(case_data: Dict[str, Any]) -> str:
    """Inserts a new case and returns its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Generate Case ID if not provided
    case_id = case_data.get("case_id")
    if not case_id:
        # Format: MG-YYYYMMDD-XXXX
        date_str = datetime.now().strftime("%Y%m%d")
        random_suffix = str(uuid.uuid4().int)[:4]
        case_id = f"MG-{date_str}-{random_suffix}"
    
    created_at = case_data.get("created_at") or datetime.utcnow().isoformat()
    follow_up_answers = case_data.get("follow_up_answers", "{}")
    if not isinstance(follow_up_answers, str):
        import json
        follow_up_answers = json.dumps(follow_up_answers)

    cursor.execute("""
        INSERT INTO cases (
            case_id, created_at, original_report, redacted_report, follow_up_answers,
            issue_type, priority, affected_group, duration, location_hint,
            assessment_summary, immediate_guidance, recommended_actions, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        case_id,
        created_at,
        case_data.get("original_report", ""),
        case_data.get("redacted_report", ""),
        follow_up_answers,
        case_data.get("issue_type", "other"),
        case_data.get("priority", "Medium"),
        case_data.get("affected_group", ""),
        case_data.get("duration", ""),
        case_data.get("location_hint", ""),
        case_data.get("assessment_summary", ""),
        case_data.get("immediate_guidance", ""),
        case_data.get("recommended_actions", ""),
        case_data.get("status", "new")
    ))
    conn.commit()
    conn.close()
    return case_id

def update_case_status(case_id: str, status: str) -> bool:
    """Updates case status. Allowed values: new, reviewing, assigned, resolved."""
    if status not in ["new", "reviewing", "assigned", "resolved"]:
        raise ValueError(f"Invalid status: {status}")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE cases SET status = ? WHERE case_id = ?",
        (status, case_id)
    )
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

def get_case(case_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def list_cases(priority: Optional[str] = None, issue_type: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM cases"
    params = []
    conditions = []
    
    if priority:
        conditions.append("priority = ?")
        params.append(priority)
    if issue_type:
        conditions.append("issue_type = ?")
        params.append(issue_type)
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        
    query += " ORDER BY created_at DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def seed_demo_data():
    """Seeds database with the demo scenarios."""
    import json
    
    # 1. Brown water near school
    case1 = {
        "case_id": "MG-DEMO-001",
        "created_at": datetime.now().isoformat(),
        "original_report": "The tap water near our elementary school is very brown since yesterday morning and children are drinking from it. We need someone to check it.",
        "redacted_report": "The tap water near our elementary school is very brown since yesterday morning and children are drinking from it. We need someone to check it.",
        "follow_up_answers": json.dumps({"q1": "Elementary school tap", "q2": "Since yesterday morning", "q3": "School children"}),
        "issue_type": "possible_contamination",
        "priority": "Critical",
        "affected_group": "School children & community",
        "duration": "Since yesterday morning",
        "location_hint": "Near the elementary school",
        "assessment_summary": "Brown water reported at an elementary school water point, with active exposure to children. Potential biological or chemical contamination.",
        "immediate_guidance": "DO NOT DRINK. Boiling may not remove chemical contaminants. Use alternative bottled water or certified safe supply immediately.",
        "recommended_actions": "1. Deploy water safety inspector to school location.\n2. Disconnect/label the tap as unsafe.\n3. Sample water for biological and heavy metal testing.",
        "status": "new"
    }
    
    # 2. Broken borehole causing long queue
    case2 = {
        "case_id": "MG-DEMO-002",
        "created_at": datetime.now().isoformat(),
        "original_report": "The main borehole in our village has stopped working completely. People are queuing since 4 AM trying to get water from the old shallow well, which is not clean.",
        "redacted_report": "The main borehole in our village has stopped working completely. People are queuing since 4 AM trying to get water from the old shallow well, which is not clean.",
        "follow_up_answers": json.dumps({"q1": "Main village borehole", "q2": "Stopped working today", "q3": "Entire village community"}),
        "issue_type": "infrastructure_failure",
        "priority": "High",
        "affected_group": "Entire village community",
        "duration": "Stopped working today, queue since 4 AM",
        "location_hint": "Main village borehole",
        "assessment_summary": "Complete failure of primary borehole infrastructure forcing community to use an unsafe secondary source (shallow well).",
        "immediate_guidance": "If using shallow well water, BOIL the water vigorously for at least one minute before drinking or cooking to kill pathogens. Store in clean, covered containers.",
        "recommended_actions": "1. Dispatch repair technician to check borehole pump mechanics.\n2. Distribute chlorine purification tablets for shallow well water in the interim.\n3. Coordinate water trucking if repair takes >48 hours.",
        "status": "reviewing"
    }
    
    # Ensure tables exist
    init_db()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    # Check if demo cases already exist
    cursor.execute("SELECT case_id FROM cases WHERE case_id IN ('MG-DEMO-001', 'MG-DEMO-002')")
    existing = [r[0] for r in cursor.fetchall()]
    conn.close()
    
    if "MG-DEMO-001" not in existing:
        create_case(case1)
    if "MG-DEMO-002" not in existing:
        create_case(case2)
