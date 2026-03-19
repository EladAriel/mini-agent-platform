import asyncio
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from arq.connections import create_pool, RedisSettings as ArqRedisSettings

from app.core.config import settings
from app.core.logging import config_logging, get_logger
from app.core.rate_limit import limiter, _rate_limit_exceeded_handler
from app.core.tracing import configure_tracing, shutdown_tracing
from app.db.db import init_db, close_db, get_db_client
from app.schemas.health import ChecksDetail, HealthResponse
from app.api.v1 import tools, agents, runs
from slowapi.errors import RateLimitExceeded


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Append hardening headers to every HTTP response.

    Headers set:
    - X-Content-Type-Options: nosniff  — prevents MIME-sniffing attacks
    - X-Frame-Options: DENY            — blocks clickjacking via iframes
    - Strict-Transport-Security        — HSTS; forces HTTPS for 1 year
    - X-XSS-Protection: 0              — disables legacy XSS filter (modern
                                         browsers use CSP; the old filter can
                                         introduce vulnerabilities)
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["X-XSS-Protection"] = "0"
        return response

config_logging()
logger = get_logger(__name__)
logger.info("Starting %s", settings.APP_NAME)

# ---------------------------------------------------------------------------
# Health router — defined at module scope so @limiter.limit() is applied once,
# not once per create_app() call (which would accumulate Limit objects and
# multiply the effective rate limit on every test-fixture app creation).
# ---------------------------------------------------------------------------
_health_router = APIRouter(tags=["Health"])


@_health_router.get("/health", response_model=HealthResponse)
@limiter.limit(settings.RATE_LIMIT_HEALTH_ENDPOINT)
async def health(request: Request, response: Response):
    db_status = "ok"
    try:
        client = get_db_client()
        if client is None:
            raise RuntimeError("DB client not initialized")
        await asyncio.wait_for(
            client.admin.command("ping"),
            timeout=2.0,
        )
    except Exception:
        db_status = "unavailable"

    ok = db_status == "ok"
    body = HealthResponse(
        status="ok" if ok else "degraded",
        checks=ChecksDetail(db=db_status),
    )
    return JSONResponse(
        content=body.model_dump(),
        status_code=200 if ok else 503,
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    if settings.OTEL_ENABLED:
        configure_tracing(app)

    if not settings.TESTING:
        app.state.arq_pool = await create_pool(
            ArqRedisSettings.from_dsn(settings.REDIS_URL)
        )
        logger.info("ARQ Redis pool connected")
    else:
        app.state.arq_pool = None  # replaced by test fixture

    yield

    if app.state.arq_pool is not None:
        await app.state.arq_pool.close()
        logger.info("ARQ Redis pool closed")

    if settings.OTEL_ENABLED:
        shutdown_tracing()

    await close_db()

description="""
### 🚀 Overview

The **Mini Agent Platform** is a multi-tenant orchestration layer designed for the lifecycle management of AI Agents. It provides a standardized interface for defining specialized personas, registering reusable toolsets, and executing complex tasks with full auditability.


### 🛠️ Key Capabilities

* **Multi-Tenancy:** Strict data isolation via `X-API-Key` validation — every resource is scoped to a tenant.
* **Agent Orchestration:** Fully async execution — `POST /agents/{id}/run` returns HTTP 202 immediately; an ARQ background worker processes the run; clients poll `GET /runs/{run_id}` until status is `completed` or `failed`.
* **Traceable Execution:** Detailed execution logs including step-by-step tool inputs, outputs, and agent reasoning traces.
* **Audit Log:** Every run lifecycle transition (`created → running → completed/failed`) is appended as an immutable `AuditEvent` document — zero updates, append-only.
* **Structured JSON Logging:** structlog-based JSON log output (machine-parseable, Datadog/ELK compatible) with `trace_id`/`span_id` injected automatically when an OTel span is active.
* **Distributed Tracing:** OpenTelemetry spans across the full HTTP → worker path, propagated via W3C `traceparent`; configurable OTLP exporter or console fallback.
* **Rate Limiting:** Three independent sliding-window strategies — per-tenant on `POST /run`, per-IP on `GET /health`, and per-IP brute-force prevention on auth failures.
* **Model Routing:** Currently runs on a deterministic mock LLM — swap in a real provider by replacing `MockChatModel` in `executor.py`.

### 🔒 Security

* **Prompt Injection Guardrail:** Every user task and tool output is scanned for override phrases, exfiltration attempts, delimiter injection, invisible characters, homoglyph substitutions, and base64-encoded payloads.
* **Secret Scanning:** Tool outputs are checked against 8 credential patterns (OpenAI keys, AWS access keys, Bearer tokens, PEM blocks, GitHub/Slack/Google tokens, generic API keys) — a match aborts the run with HTTP 500 before any data is persisted.
* **PII Anonymization:** Presidio detects and redacts 8 entity types (SSN, ITIN, credit card, email, phone, person name, location, date of birth) in inputs, tool outputs, and final responses before anything is written to the database.
* **Security Headers:** `SecurityHeadersMiddleware` appends `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`, and `X-XSS-Protection` to every response.
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
    app.include_router(_health_router)

    # CORS — must be added before SecurityHeadersMiddleware so that CORS
    # logic (Vary: Origin, preflight handling) runs first.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["X-API-Key", "Content-Type"],
    )

    # Security headers — outermost wrapper; appended last so Starlette
    # (LIFO middleware stack) processes it before CORS.
    app.add_middleware(SecurityHeadersMiddleware)

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    @app.get("/", include_in_schema=False)
    async def root():
        return RedirectResponse(url="/docs")

    return app

app = create_app()