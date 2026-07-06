import sys
import os
import logging
import asyncio
from typing import AsyncGenerator
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.pii_service import redact_pii
from app.agents.specialists import (
    intake_agent,
    clarification_agent,
    risk_priority_agent,
    knowledge_agent,
    case_coordinator_agent
)

logger = logging.getLogger("majiguard.coordinator")

class MajiGuardCoordinator(BaseAgent):
    """Orchestrates MajiGuard specialized agents to triage water issues."""
    
    def __init__(self, name: str = "MajiGuardCoordinator"):
        super().__init__(name=name)

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        state = ctx.session.state
        
        # Initialize default session state keys to avoid KeyErrors in specialist templates
        state.setdefault("intake_data", {})
        state.setdefault("clarification_result", {})
        state.setdefault("priority_result", {})
        state.setdefault("immediate_guidance", "")
        state.setdefault("redacted_report", "")
        
        # Get user's current message
        user_message = ""
        if ctx.user_content and ctx.user_content.parts:
            user_message = "".join(p.text for p in ctx.user_content.parts if p.text)
            
        if not user_message.strip():
            yield Event(author=self.name, text="Please submit a water access or water safety issue.")
            return

        # Load session variables
        original_report = state.get("original_report", "")
        questions_asked = state.get("questions_asked", 0)
        follow_up_answers = state.get("follow_up_answers", {})

        if not original_report:
            # First turn: User submitted the original report
            original_report = user_message
            state["original_report"] = original_report
            state["redacted_report"] = redact_pii(original_report)
            state["follow_up_answers"] = {}
            state["questions_asked"] = 0
            logger.info(f"First turn. Redacted report: {state['redacted_report']}")
        else:
            # Subsequent turn: User is replying to a follow-up clarification question
            q_index = f"q{questions_asked}"
            follow_up_answers[q_index] = user_message
            state["follow_up_answers"] = follow_up_answers
            logger.info(f"Follow-up answer {q_index}: {user_message}")

        # Step 1: Run IntakeAgent to extract details
        logger.info("Invoking IntakeAgent...")
        await asyncio.sleep(17)
        async for _ in intake_agent.run_async(ctx):
            pass
        
        intake_data = state.get("intake_data")
        # Ensure intake_data is stored as a dictionary
        if hasattr(intake_data, "model_dump"):
            intake_data = intake_data.model_dump()
            state["intake_data"] = intake_data
        logger.info(f"Intake data: {intake_data}")

        # Step 2: Run ClarificationAgent to check for missing info
        logger.info("Invoking ClarificationAgent...")
        await asyncio.sleep(17)
        async for _ in clarification_agent.run_async(ctx):
            pass
            
        clarification_result = state.get("clarification_result")
        if hasattr(clarification_result, "model_dump"):
            clarification_result = clarification_result.model_dump()
            state["clarification_result"] = clarification_result
        logger.info(f"Clarification result: {clarification_result}")

        # Check if we should ask a follow-up question
        follow_up_question = None
        if clarification_result and isinstance(clarification_result, dict):
            follow_up_question = clarification_result.get("follow_up_question")
            
        if follow_up_question and follow_up_question.strip() and questions_asked < 3:
            # Ask the follow-up question
            state["questions_asked"] = questions_asked + 1
            yield Event(author=self.name, text=follow_up_question)
            return

        # If we have enough info or reached the 3-question limit, run remaining triage agents
        logger.info("Proceeding to final triage...")
        
        # Step 3: Run RiskPriorityAgent
        logger.info("Invoking RiskPriorityAgent...")
        await asyncio.sleep(17)
        async for _ in risk_priority_agent.run_async(ctx):
            pass
        
        priority_result = state.get("priority_result")
        if hasattr(priority_result, "model_dump"):
            priority_result = priority_result.model_dump()
            state["priority_result"] = priority_result
        logger.info(f"Priority result: {priority_result}")

        # Step 4: Run KnowledgeAgent
        logger.info("Invoking KnowledgeAgent...")
        await asyncio.sleep(17)
        async for _ in knowledge_agent.run_async(ctx):
            pass
        logger.info(f"Immediate Guidance: {state.get('immediate_guidance')}")

        # Step 5: Run CaseCoordinatorAgent
        logger.info("Invoking CaseCoordinatorAgent...")
        final_text = ""
        await asyncio.sleep(17)
        async for event in case_coordinator_agent.run_async(ctx):
            if event.content and event.content.parts:
                final_text += "".join(p.text for p in event.content.parts if p.text)
                
        # Yield the final compiled response
        yield Event(author=self.name, text=final_text)
