# MajiGuard Architecture

This document describes the structural and multi-agent design of **MajiGuard**, an AI water-access triage MVP built for the Kaggle Capstone Project.

## System Overview

MajiGuard consists of a React frontend and a FastAPI backend that hosts a Google ADK-powered multi-agent system. Case management and water-support knowledge lookups are handled through a local **Model Context Protocol (MCP)** server, which coordinates database access and semantic articles.

## Component Architecture

Below is the Mermaid sequence and structure diagram of MajiGuard:

```mermaid
graph TD
    subgraph Client ["Client Layer (Frontend)"]
        UI["React Web UI (Vite + TS)"]
        Chat["Chat Interface (Plain Text)"]
        Dash["Triage Dashboard (Filters, Detail Panel)"]
        UI --> Chat
        UI --> Dash
    end

    subgraph Server ["FastAPI Backend Server"]
        API["FastAPI Web Framework"]
        RateLimit["Rate Limiter (In-Memory sliding window)"]
        PII["PII Redaction Service (Regex + Pattern matching)"]
        API --> RateLimit
        API --> PII
    end

    subgraph Agents ["ADK Multi-Agent System"]
        Coord["MajiGuardCoordinator (BaseAgent Orchestrator)"]
        Intake["IntakeAgent (JSON extraction & classification)"]
        Clarify["ClarificationAgent (Follow-up detection, max 3 questions)"]
        Priority["RiskPriorityAgent (Deterministic rules + LLM)"]
        Knowledge["KnowledgeAgent (MCP-driven safety lookup)"]
        CaseCoord["CaseCoordinatorAgent (Case saving & summary compiler)"]
        
        Coord --> Intake
        Coord --> Clarify
        Coord --> Priority
        Coord --> Knowledge
        Coord --> CaseCoord
    end

    subgraph MCP ["Model Context Protocol (MCP) Layer"]
        MCPServer["Python MCP Server (FastMCP stdio)"]
        T1["search_guidance() tool"]
        T2["create_case() tool"]
        T3["update_case_status() tool"]
        T4["list_cases() tool"]
        T5["get_case() tool"]
        
        MCPServer --> T1
        MCPServer --> T2
        MCPServer --> T3
        MCPServer --> T4
        MCPServer --> T5
    end

    subgraph Storage ["Data & Knowledge Layer"]
        DB["SQLite DB (cases table)"]
        KB["Local Knowledge Base (JSON articles)"]
    end

    subgraph LLM ["External LLM Layer"]
        Gemini["Gemini 2.5 Flash (via AI Studio GEMINI_API_KEY)"]
    end

    %% Flows & Connections
    Chat -->|POST /api/chat| API
    Dash -->|GET /api/cases| API
    Dash -->|POST /api/cases/:id/status| API
    
    API -->|Runner| Coord
    
    Intake -->|generate_content| Gemini
    Clarify -->|generate_content| Gemini
    Priority -->|generate_content| Gemini
    
    Knowledge -->|MCP Stdio Tool| T1
    CaseCoord -->|MCP Stdio Tool| T2
    
    T1 --> KB
    T2 & T3 & T4 & T5 --> DB
    
    style Client fill:#f9f9f9,stroke:#333,stroke-width:2px
    style Server fill:#f0f7ff,stroke:#0284c7,stroke-width:2px
    style Agents fill:#faf5ff,stroke:#a855f7,stroke-width:2px
    style MCP fill:#ecfdf5,stroke:#10b981,stroke-width:2px
    style Storage fill:#fefaf0,stroke:#f59e0b,stroke-width:2px
```

## Detailed Agent Workflow

1. **Intake & Redaction**: The user report is sent to the `MajiGuardCoordinator`. PII (emails, phone numbers) is instantly redacted via Python services. The `IntakeAgent` extracts location, affected group, alternative water sources, and classifies the issue.
2. **Missing Information Check**: The `ClarificationAgent` checks if critical variables (such as location/landmark, issue duration, or affected numbers) are missing. If so, and we have asked fewer than three questions, the coordinator pauses the flow and prompts the user.
3. **Priority Triage**: Once complete, the `RiskPriorityAgent` determines case severity (Low, Medium, High, Critical) combining safety rules with Gemini's reasoning.
4. **Knowledge Retrieval**: The `KnowledgeAgent` uses the `search_guidance` MCP tool to search for matching community safety articles.
5. **Incident Finalization**: The `CaseCoordinatorAgent` compiles all details, calls the `create_case` MCP tool to save the case to the SQLite database, and returns the case summary and ID to the user.
