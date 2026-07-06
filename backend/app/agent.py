from google.adk.apps import App
from app.agents.coordinator import MajiGuardCoordinator

# The root agent is our orchestrator coordinator agent
root_agent = MajiGuardCoordinator()

# The ADK App wrapper
app = App(
    root_agent=root_agent,
    name="app",
)
