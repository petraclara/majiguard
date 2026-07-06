import sys
import os
from typing import Literal, Optional, List
from pydantic import BaseModel, Field
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# Configure Model
model_name = "gemini-2.5-flash"
model = Gemini(model=model_name)

# Expose MCP Tools to agents
mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=["-m", "app.mcp_server.server"],
        ),
    ),
)

# 1. IntakeAgent Structured Schema
class IntakeData(BaseModel):
    location_hint: Optional[str] = Field(description="Any location name, landmark, village, town, or school mentioned in the report.")
    issue_type: Literal["possible_contamination", "infrastructure_failure", "water_shortage", "long_queue_or_access_issue", "other"] = Field(
        description="Classification of the issue."
    )
    affected_group: Optional[str] = Field(description="Who is affected, e.g. children, schools, village, clinics, many people.")
    duration: Optional[str] = Field(description="How long the water issue has been going on, e.g. three days, since morning.")
    safety_concerns: Optional[str] = Field(description="Any symptoms like sickness, diarrhea, or risks like drinking unsafe water.")
    alternative_water: Optional[str] = Field(description="Whether alternative water is available, e.g. old shallow well, river, none.")

# IntakeAgent Agent
intake_agent = Agent(
    name="IntakeAgent",
    model=model,
    instruction="""You are the IntakeAgent for MajiGuard.
Your task is to analyze the user's water issue report and extract structured information.
Focus on identifying the location, issue type, affected group, duration, safety concerns, and alternative water sources.
Also, redact full names, email addresses, and phone numbers to maintain privacy.
Return your output matching the IntakeData schema.
""",
    output_schema=IntakeData,
    output_key="intake_data"
)


# 2. ClarificationAgent Structured Schema
class ClarificationResult(BaseModel):
    missing_fields: List[str] = Field(description="List of critical fields that are missing (from: location, issue_type, affected_group, duration).")
    follow_up_question: Optional[str] = Field(
        description="ONE polite, empathetic question to ask the user to clarify ONE missing detail. Return empty string if no follow-up is needed or if we have hit the question limit."
    )

# ClarificationAgent Agent
clarification_agent = Agent(
    name="ClarificationAgent",
    model=model,
    instruction="""You are the ClarificationAgent for MajiGuard.
Analyze the extracted intake data and check if any critical details (location, issue_type, affected_group, duration) are missing.
If critical information is missing, generate ONE clear, polite, and empathetic follow-up question.
Do not ask for sensitive personal data (e.g. phone numbers, email addresses, full names).
Return your output matching the ClarificationResult schema.
""",
    output_schema=ClarificationResult,
    output_key="clarification_result"
)


# 3. RiskPriorityAgent Structured Schema
class RiskPriorityResult(BaseModel):
    priority: Literal["Low", "Medium", "High", "Critical"] = Field(description="Determined priority level.")
    reasoning: str = Field(description="Brief, clear explanation of the priority decision based on the rules.")

# RiskPriorityAgent Agent
risk_priority_agent = Agent(
    name="RiskPriorityAgent",
    model=model,
    instruction="""You are the RiskPriorityAgent for MajiGuard.
Your task is to assign a priority level (Low, Medium, High, or Critical) based on the water issue details.

Follow these rules:
- Possible contamination affecting children, schools, clinics, or many people: High or Critical.
- No water for multiple days with no alternative source: High.
- Broken water point with alternative sources available: Medium.
- Long queues without immediate safety risk: Low or Medium.
- Other general issues: Low.

Return your output matching the RiskPriorityResult schema.
""",
    output_schema=RiskPriorityResult,
    output_key="priority_result"
)


# 4. KnowledgeAgent Agent
knowledge_agent = Agent(
    name="KnowledgeAgent",
    model=model,
    tools=[mcp_toolset],
    instruction="""You are the KnowledgeAgent for MajiGuard.
Your task is to search the local water-support knowledge base for safe, practical guidance matching the reported issue.
Use the `search_guidance` tool to query the knowledge base.
Provide clear, actionable safety instructions.
Always include a clear disclaimer stating: "MajiGuard provides general information and triage guidance. It does not replace professional water testing, medical advice, or local water authorities."
Do not propose complex chemical treatments; keep guidance safe and general.
""",
    output_key="immediate_guidance"
)


# 5. CaseCoordinatorAgent Agent
case_coordinator_agent = Agent(
    name="CaseCoordinatorAgent",
    model=model,
    tools=[mcp_toolset],
    instruction="""You are the CaseCoordinatorAgent for MajiGuard.
Compile all information gathered by the other agents:
- Original & Redacted Report: {redacted_report}
- Intake Data: {intake_data}
- Priority & Reasoning: {priority_result}
- Immediate Guidance: {immediate_guidance}

Perform the following:
1. Save the structured case in the database by calling the `create_case` tool.
   Construct a case_data dictionary containing all these fields.
2. Formulate a concise, user-safe "assessment_summary" (do NOT expose raw chain-of-thought or reasoning).
3. Produce the final structured response showing:
   * Case ID: [Returned by create_case]
   * Issue Type: [Extracted issue type]
   * Priority: [Priority level]
   * Affected Group: [Extracted group]
   * Reported Duration: [Extracted duration]
   * Immediate Safety Guidance: [Retrieved guidance]
   * Recommended Next Steps: [Actionable recommendations for user and support team]
Include a clear disclaimer that MajiGuard is a triage tool, not an emergency/medical service.
""",
    output_key="coordinator_response"
)
