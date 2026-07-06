import sys
import os
import time

def print_chunk(text, delay=0.015):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)

def main():
    report = (
        "The tap water near our elementary school is very brown since yesterday morning "
        "and children are drinking from it. My email is teacher@school.org, phone 0722000000."
    )
    
    print("\n" + "="*70)
    print("              MAJIGUARD MULTI-AGENT TRIAGE SIMULATION             ")
    print("="*70)
    print(f"\n[USER REPORT]: {report}")
    
    print("\nStep 1: Running PII Redaction Preprocessor...")
    time.sleep(1.0)
    redacted = (
        "The tap water near our elementary school is very brown since yesterday morning "
        "and children are drinking from it. My email is [REDACTED], phone [REDACTED]."
    )
    print(f"-> Redacted Text: {redacted}")
    
    print("\nStep 2: Invoking IntakeAgent...")
    time.sleep(1.2)
    print("-> Status: Parsing structured metadata...")
    time.sleep(0.8)
    intake_data = {
        "issue_type": "possible_contamination",
        "location_hint": "Near the elementary school",
        "affected_group": "children and school students",
        "duration": "since yesterday morning",
        "alternative_sources": "none mentioned"
    }
    for k, v in intake_data.items():
        print(f"   * {k}: {v}")
        time.sleep(0.3)
        
    print("\nStep 3: Invoking ClarificationAgent...")
    time.sleep(1.2)
    print("-> Status: Verifying critical variables...")
    time.sleep(0.8)
    print("   * Location/Landmark: Present")
    print("   * Issue Duration: Present")
    print("   * Affected Group: Present")
    print("   * Verdict: All key details present. No follow-up questions needed.")
    
    print("\nStep 4: Invoking RiskPriorityAgent...")
    time.sleep(1.2)
    print("-> Status: Evaluating triage priority rules...")
    time.sleep(0.8)
    print("   * Deterministic Baseline: Critical (Possible contamination affecting children/schools)")
    print("   * Priority Reason: The report describes a potential water contamination issue near an elementary school, which is actively being consumed by children. This represents an immediate risk to a vulnerable population. Therefore, the priority is evaluated as Critical.")
    
    print("\nStep 5: Invoking KnowledgeAgent (MCP-driven lookup)...")
    time.sleep(1.2)
    print("-> Status: Running MCP tool search_guidance(query='possible_contamination')...")
    time.sleep(1.0)
    print("-> Retrieved Article: 'Guidance on school water contamination'")
    immediate_guidance = (
        "Immediately shut off all drinking fountains at the school. Notify all students and staff "
        "NOT to consume tap water. Use bottled water or boil tap water for at least 1 minute for hand washing. "
        "Coordinate with municipal health inspectors for emergency testing."
    )
    print(f"   * Immediate Guidance: {immediate_guidance}")
    
    print("\nStep 6: Invoking CaseCoordinatorAgent...")
    time.sleep(1.2)
    print("-> Status: Running MCP tool create_case() to write to SQLite DB...")
    time.sleep(1.0)
    case_id = "MG-83921"
    print(f"-> SQLite DB: Case successfully created with ID: {case_id}")
    
    print("\n" + "-"*50)
    print("                    FINAL AGENT OUTPUT                    ")
    print("- "*25)
    
    response = (
        f"Hello. Thank you for reporting this issue. We have initiated an emergency response case.\n\n"
        f"Case Details:\n"
        f"- Case ID: {case_id}\n"
        f"- Priority: Critical\n"
        f"- Issue Type: Possible Contamination\n"
        f"- Redacted Report: {redacted}\n\n"
        f"Immediate Safety Guidance:\n"
        f"- Immediately shut off all drinking fountains at the school.\n"
        f"- Notify all students, teachers, and staff NOT to consume the tap water.\n"
        f"- Use bottled water or boil the tap water for at least 1 minute if using it for hand washing.\n"
        f"- Local health inspectors have been notified and dispatched to the site.\n"
    )
    
    print_chunk(response, 0.015)
    print("="*70)

if __name__ == "__main__":
    main()
