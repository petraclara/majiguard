# MajiGuard — AI Water-Access Triage Portal

**MajiGuard** is a polished, runnable full-stack MVP designed as an **Agents for Good** submission for the Kaggle *“AI Agents: Intensive Vibe Coding Capstone Project.”* 

Its purpose is to help community members report water-access and water-safety issues in natural language, automatically sanitizing reports and triaging them into prioritized, structured incident cases for a water-support team.

---

## 🚀 Features

1. **Intelligent Intake & Clarification**: A multi-agent coordinator that parses reports, detects missing critical data (location, duration, affected group), and dynamically prompts the user with up to three polite follow-up questions.
2. **Transparent Priority Triage**: Blends deterministic safety rules (e.g. possible contamination affecting children/schools -> Critical priority) with LLM judgment to classify severity.
3. **Model Context Protocol (MCP) Server**: Hosts case management tools and local safety guidelines over a python standard-input/output connection, serving as a standardized database/knowledge access layer.
4. **Support Dashboard**: A split-screen dashboard allowing engineers to search, filter by priority and type, inspect case detail files (including original/redacted text and clarification Q&A), and update case statuses.
5. **Security & Privacy Guards**: Automatic deterministic PII redaction (email/phone number stripping) before saving to the database, basic rate limiting, and user disclaimers.

---

## 📂 Project Structure

```text
majiguard/
├── backend/
│   ├── app/
│   │   ├── agents/          # Specialized ADK agents & coordinator definitions
│   │   ├── mcp_server/      # FastMCP python server exposing database & KB tools
│   │   ├── services/        # SQLite DB, PII redaction, and priority rules
│   │   └── data/            # SQLite database file and raw KB articles
│   ├── Dockerfile           # Backend container setup
│   ├── main.py              # FastAPI endpoints & rate-limit configuration
│   ├── requirements.txt     # Backend python dependencies
│   └── tests/               # Unit and integration test suites
├── frontend/
│   ├── src/                 # React components (App.tsx, App.css)
│   ├── Dockerfile           # Multi-stage Nginx production build
│   ├── package.json         # Node dependencies
│   └── index.html           # Main HTML entrypoint (SEO optimized)
├── docs/
│   ├── architecture.md      # Detailed Mermaid architecture diagrams
│   └── demo-script.md       # 5-minute Kaggle presentation script
├── docker-compose.yml       # Local orchestration for full stack
├── .env.example             # Template for API keys
└── README.md                # This documentation
```

---

## 🛠️ Installation & Local Setup

### 1. Prerequisites
Ensure you have the following installed on your machine:
*   **Python 3.11+**
*   **Node.js v18+ & npm**
*   **Gemini API Key** (obtainable from [Google AI Studio](https://aistudio.google.com/app/apikey))

### 2. Configure Environment Variables
Copy `.env.example` to `.env` in the root folder:
```bash
cp .env.example .env
```
Open `.env` and insert your API Key:
```bash
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Install Backend Dependencies
Navigate to the `backend/` directory, set up a virtual environment, and install dependencies:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies
Navigate to the `frontend/` directory and install npm packages:
```bash
cd ../frontend
npm install
```

---

## 🖥️ Running the Application

### Option A: Running Locally (Development Mode)

1.  **Start the Backend**:
    From the `backend/` directory (with your virtualenv active):
    ```bash
    python main.py
    ```
    The FastAPI backend will start at **`http://localhost:8000`**. You can access the Swagger docs at `http://localhost:8000/docs`.

2.  **Start the Frontend**:
    From the `frontend/` directory:
    ```bash
    npm run dev
    ```
    The Vite server will start, typically at **`http://localhost:5173`**. Open this URL in your browser.

---

### Option B: Running via Docker Compose (Recommended)

To run the entire full-stack app inside isolated containers with persistent database storage, run this single command at the project root:
```bash
docker-compose up --build
```
*   **Frontend Access**: `http://localhost:8080`
*   **Backend Access**: `http://localhost:8000`

---

## 🧪 Testing

We have built a robust unit test suite covering **PII redaction, case creation/database operations, and priority triage rules**. 

To execute the test suite (from the project root):
```bash
PYTHONPATH=backend python -m pytest backend/tests
```

---

## 🔌 Model Context Protocol (MCP) Integration

Rather than hard-coupling agents to direct file system or SQL libraries, MajiGuard utilizes an **MCP Server** built with `FastMCP` that communicates over `stdio`. The agents utilize the ADK `McpToolset` to dynamically execute these tools:

*   `search_guidance(query: str)`: Queries local JSON water safety articles.
*   `create_case(case_data: dict)`: Writes triaged cases to the SQLite DB.
*   `update_case_status(case_id: str, status: str)`: Modifies case status.
*   `list_cases(priority, issue_type)`: Fetches matching logs for the dashboard.
*   `get_case(case_id)`: Fetches detailed information on a single case.

---

## 🔒 Security & Privacy Practices

*   **PII Redaction Layer**: A deterministic regex-based preprocessor strips email addresses and phone numbers. The `IntakeAgent` additionally removes likely full names before cases are committed.
*   **Input Protection**: Backend APIs restrict text submissions to **1000 characters** to protect against prompt injection or memory exhaustion.
*   **Rate Limiting**: An in-memory sliding window allows a maximum of 10 requests per minute per IP address.
*   **Triage Disclaimer**: The UI and coordinator output clearly display disclaimers stating that MajiGuard is an information-routing assistant and does *not* replace emergency municipal services or professional water testing.

---

## ☁️ Deployment

For deployment, the application supports switching to Google Cloud **Vertex AI** by configuring `GOOGLE_GENAI_USE_VERTEXAI=true` and setting the GCP project details in your environment. Detailed Terraform scripts and CI/CD workflows can be added by running:
```bash
agents-cli scaffold enhance . --deployment-target cloud_run
```
