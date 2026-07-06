# MajiGuard Video Demonstration Script
**Time-Stamped Script for the 5-Minute Kaggle AI Agents Capstone Video Demo**

---

### **[0:00 - 0:45] Section 1: Introduction & Problem Statement**
* **Visual**: Show the browser screen on the MajiGuard home page. The cursor hovers over the brand title.
* **Audio / Speak**:
  > "Hello everyone! This is MajiGuard, an 'Agents for Good' entry for the Kaggle AI Agents Intensive Capstone. 
  > In many developing regions, community members report water-access and water-safety issues using plain, unstructured language—often via SMS or local chat threads. 
  > Support teams get overwhelmed by these unstructured messages and struggle to prioritize them.
  > MajiGuard solves this by deploying a Google ADK multi-agent system and a Model Context Protocol—or MCP—server. It turns raw natural language reports into structured, prioritized, and actionable cases for local water-support teams, while providing immediate, safe guidance to the reporter."

---

### **[0:45 - 1:45] Section 2: Architecture & Setup**
* **Visual**: Show the `docs/architecture.md` Mermaid diagram, then quickly toggle to the terminal to show `main.py` and the SQLite database.
* **Audio / Speak**:
  > "MajiGuard is built on a clean, modern full-stack architecture. 
  > On the frontend, we use React with Vite and TypeScript. 
  > The backend runs a FastAPI server, orchestrating five specialized ADK agents through the `MajiGuardCoordinator`. 
  > For persistence and data access, we wrote a Python MCP server using FastMCP. The agents call these tools over stdio to query the SQLite database and search a local water-safety knowledge base. 
  > Finally, we enforce security filters like PII redaction and rate limiting directly in our Python pipeline."

---

### **[1:45 - 3:00] Section 3: Live Triage Demo (Scenario 1: Contamination)**
* **Visual**: Switch back to the React UI. Click the first quick-start button: *"The tap water near our elementary school is very brown since yesterday morning and children are drinking from it."* Click Send.
* **Audio / Speak**:
  > "Let's run our first demo scenario: brown water near a school. 
  > As soon as the user submits the report, the MajiGuardCoordinator sanitizes PII and triggers the IntakeAgent. 
  > It extracts the issue type, but detects that critical details are missing. The ClarificationAgent steps in, and generates an empathetic follow-up question.
  > Let's reply: 'The school is located next to the village clinic, and children are complaining of stomach pain.' 
  > The agent receives the response, updates the intake model, and completes the triage. 
  > Since this involves potential contamination affecting school children, it automatically triggers a Critical priority. 
  > The CaseCoordinatorAgent invokes the MCP tool to save the case and prints a user-safe triage summary with immediate safety guidance and recommended next steps."

---

### **[3:00 - 4:00] Section 4: Live Triage Demo (Scenario 2: Infrastructure Outage)**
* **Visual**: Click 'Load Demo Scenarios' in the top bar. Show the cases dashboard on the right populating with two pre-loaded cases. Search for 'borehole'.
* **Audio / Speak**:
  > "On the right side of the portal, we have our Support Team Dashboard. 
  > I've clicked 'Load Demo Scenarios', which calls our `/api/demo/load` endpoint to seed the SQLite database. 
  > Here, we see another scenario: a broken borehole causing a long queue.
  > Let's open this case. Support engineers can view the full case file—including the original report, the PII-redacted text, and the agent's concise 'assessment summary' that hides inner LLM chain-of-thought.
  > The dashboard lets team members filter cases by priority and type, and update the status in real time. 
  > When I change the status from 'Reviewing' to 'Assigned', the frontend communicates with the backend, which delegates the database update to the MCP server."

---

### **[4:00 - 4:45] Section 5: Under the Hood - MCP & Security**
* **Visual**: Show the code of `pii_service.py` and `server.py` (MCP tools) in the IDE.
* **Audio / Speak**:
  > "Under the hood, security and local persistence are core priorities. 
  > Our `pii_service` uses deterministic regex patterns to strip emails and phone numbers before the report ever touches the database, protecting community privacy. 
  > Rather than coupling agents directly to the database, our ADK agents use MCP stdio tools to execute database operations. 
  > The MCP server serves as a clean, standardized data access layer, decoupling our LLM agents from the underlying SQL tables."

---

### **[4:45 - 5:00] Section 6: Conclusion**
* **Visual**: Show the full UI, both chat and dashboard side-by-side.
* **Audio / Speak**:
  > "In summary, MajiGuard is a polished, full-stack capstone MVP demonstrating multi-agent workflows, real-time local database persistence via MCP, and critical privacy safety nets. 
  > It is fully containerized with Docker and ready for local runs. 
  > Thank you for watching, and let's guard our water resources together!"
