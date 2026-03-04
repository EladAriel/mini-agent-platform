# Architecture

High-level overview of the full system — from Docker infrastructure to request handling.

---

## Docker Infrastructure

```mermaid
flowchart TD
    ENV[.env file] --> MC[mongo container\nmongo:8.2]
    ENV --> AC[api container\npython:3.12-slim]

    MC --> VOL[(mongo_data volume)]
    MC --> INIT[mongo-init.js\ncreates app_user]

    AC --> APP[uvicorn\napp.main:app\n:8000]
    AC -->|depends_on healthy| MC

    subgraph app_network
        MC
        AC
    end
```

Two services share a bridge network. The API waits for MongoDB's healthcheck to pass before starting.

---

## Application Startup

`main.py` creates the FastAPI app and registers everything via a lifespan context:

```mermaid
flowchart LR
    A[create_app] --> B[Register routers /api/v1/tools /api/v1/agents /api/v1/runs]
    A --> C[lifespan]
    C --> D[init_db\connect PyMongo\init Beanie]
    D --> E[App ready]
    E --> F[shutdown\close_db]
```

---

## Core Components

```mermaid
flowchart TD
    ENV2[.env / env vars] --> CFG[config.py\Pydantic Settings]
    CFG --> SEC[security.py\resolve_tenant]
    CFG --> DB[db.py\init_beanie]
    CFG --> EX[executor.py\MAX_EXECUTION_STEPS]
    CFG --> LOG[logging.py\LOG_LEVEL]

    SEC -->|tenant_id| API[API Routes]
    DB --> MDL[Beanie Models: Tool, Agent, AgentRun]
    MDL --> MONGO[(MongoDB)]
```

`config.py` is the single source of truth for all settings — everything else reads from it.

---

## Full Request Lifecycle

```mermaid
flowchart TD
    Client -->|X-API-Key header| SEC2[resolve_tenant\security.py]
    SEC2 -- 401 --> Client
    SEC2 -->|tenant_id| RT[API Route: /tools, /agents, /runs]
    RT --> SV[Service Layer: tool_service, agent_service, run_service]
    SV --> ORM[Beanie ODM]
    ORM --> MONGO2[(MongoDB)]
    MONGO2 --> ORM
    ORM --> SV
    SV --> RT
    RT --> Client
```

---

## Agent Run Lifecycle

The most complex flow — triggered by `POST /agents/{id}/run`:

```mermaid
flowchart TD
    A[RunRequest: task + model] --> B[resolve_tenant]
    B --> C[get_agent: 404 guard]
    C --> D[guardrail: check_for_injection]
    D -- 400 --> Z[Error]
    D --> E[create_react_agent: MockLLM + tools]
    E --> F{LLM step}
    F -->|tool_call| G[ToolNode: executes tool]
    G --> H[check_tool_output: guardrail]
    H -- 400 --> Z
    H -->|safe output| F
    F -->|final answer| I[Build AgentRun]
    I --> J[(MongoDB: agent_runs)]
    I --> K[RunResponse]
```

---

## Layer Summary

| Layer | Files | Responsibility |
|-------|-------|---------------|
| **Config** | `core/config.py` | Load and validate all env vars via Pydantic Settings |
| **Logging** | `core/logging.py` | Configure stdlib logging; provide `get_logger()` |
| **Security** | `core/security.py` | Validate API key → return tenant_id |
| **App entry** | `main.py` | Create FastAPI app, register routers, manage DB lifecycle |
| **API** | `api/v1/` | HTTP routing, request/response serialisation |
| **Schemas** | `schemas/` | Pydantic validation for all inputs and outputs |
| **Services** | `services/` | Business logic, DB queries, agent orchestration |
| **Models** | `models/` | Beanie ODM documents → MongoDB collections |
| **Runner** | `services/runner/` | LangGraph execution, mock LLM, tools, guardrail |