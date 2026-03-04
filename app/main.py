from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.core.logging import config_logging, get_logger
from app.db.db import init_db, close_db
from app.api.v1 import tools, agents, runs

config_logging()
logger = get_logger(__name__)
logger.info("Starting %s", settings.APP_NAME)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    yield

    await close_db()

description="""
### 🚀 Overview

The **Mini Agent Platform** is a multi-tenant orchestration layer designed for the lifecycle management of AI Agents. It provides a standardized interface for defining specialized personas, registering reusable toolsets, and executing complex tasks with full auditability.


### 🛠️ Key Capabilities

* **Multi-Tenancy:** Strict data isolation via `X-API-Key` validation — every resource is scoped to a tenant.
* **Agent Orchestration:** Decoupled architecture allowing many-to-many relationships between agents and tools.
* **Traceable Execution:** Detailed execution logs including step-by-step tool inputs, outputs, and agent reasoning traces.
* **Model Routing:** Built-in support for routing to OpenAI and Anthropic models. Currently runs on a deterministic mock LLM — swap in a real provider by replacing `MockChatModel` in `executor.py`.

### 🔒 Security

* **Prompt Injection Guardrail:** Every user task and tool output is scanned for override phrases, exfiltration attempts, delimiter injection, invisible characters, homoglyph substitutions, and base64-encoded payloads.
* **Structural Constraints:** Input lengths are enforced at the schema level to mitigate resource exhaustion before requests reach business logic.

---
**Developer:** Elad Ariel

"""

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description=description,
        summary="A multi-tenant orchestration layer for managing AI agents, tool registries, and traceable execution runs.",
        version="1.0.0",
        lifespan=lifespan,
        openapi_tags=[
            {
                "name": "Tools",
                "description": "Manage reusable tools that agents can invoke",
            },
            {
                "name": "Agents",
                "description": "Create, manage, and execute AI agents with assigned tools",
            },
            {
                "name": "Runs",
                "description": "View execution history and run records across all agents",
            },
            {
                "name": "Health",
                "description": "Health check and monitoring endpoints",
            },
        ],        
    )

    prefix = "/api/v1"
    app.include_router(tools.router, prefix=prefix)
    app.include_router(agents.router, prefix=prefix)
    app.include_router(runs.router, prefix=prefix)
        
    @app.get("/", include_in_schema=False)
    async def root():
        return RedirectResponse(url="/docs")
        
    @app.get("/health", tags=["Health"])
    async def health():
        return {
            "status": "OK"
        }
    
    return app

app = create_app()