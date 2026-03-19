# Architecture

High-level overview of the full system — from Docker infrastructure to request handling.

---

## Docker Infrastructure

```mermaid
flowchart TD
    ENV[.env file] --> MC[mongo container: mongo:8.2]
    ENV --> AC[api container: python:3.12-slim]
    ENV --> RC[redis container: redis:7-alpine]
    ENV --> WC[worker container: python:3.12-slim]

    MC --> VOL[(mongo_data volume)]
    MC --> INIT[mongo-init.js: creates app_user]

    AC --> APP[uvicorn app.main:app:8000]
    AC -->|depends_on healthy| MC
    AC -->|depends_on healthy| RC

    RC --> RDATA[(redis queue)]

    WC --> ARQ[arq app.worker.WorkerSettings]
    WC -->|depends_on healthy| MC
    WC -->|depends_on healthy| RC

    subgraph app_network
        MC
        AC
        RC
        WC
    end
```

Four services share a bridge network. The API and worker both wait for MongoDB and Redis healthchecks to pass before starting. The worker has no exposed ports — it only needs outbound connections to Redis and MongoDB.

---

## Application Startup

`main.py` creates the FastAPI app and registers everything via a lifespan context:

```mermaid
flowchart LR
    A[create_app] --> B[Register routers: /api/v1/tools /api/v1/agents /api/v1/runs]
    A --> C[lifespan]
    C --> D[init_db\connect PyMongo\init Beanie]
    D --> T[configure_tracing\nTracerProvider + FastAPI + PyMongo]
    T --> P[create_pool ARQ\connect Redis]
    P --> E[App ready]
    E --> F[shutdown\nshutdown_tracing\nclose pool\nclose_db]
```

---

## Core Components

`config.py` is the single source of truth for all settings — everything else reads from it.

### Config Wiring

```mermaid
flowchart TD
    ENV[.env / env vars] --> CFG[config.py]
    CFG --> SEC[security.py]
    CFG --> DB[db.py]
    CFG --> LOG[logging.py / tracing.py]
    CFG --> EX[executor.py]
    CFG --> RL[rate_limit.py]
```

Detailed flows for the request and execution pipelines follow below.

### Request Pipeline

```mermaid
flowchart LR
    REQ[Incoming Request] --> SEC[security.py\nresolve_tenant]
    SEC -->|tenant_id| CTX[context.py\ntenant_ctx ContextVar]
    SEC -->|request.state.tenant_id| RL[rate_limit.py\n@limiter.limit]
    CTX --> LOG[logging.py\nTenantContextFilter]
    LOG --> OTEL[_add_otel_trace_context\ntrace_id + span_id in logs]
    RL -->|429 if exceeded| ERR[429 Too Many Requests]
    RL -->|under limit| EP[Endpoint Handler]
```

### Execution Pipeline

```mermaid
flowchart TD
    EX[executor.py] --> GR[guardrail.py\ninjection + secret checks]
    EX --> PII[pii.py\nanonymize_text]
    EX --> AS[agent_service.py\nbuild ReAct agent]
    EX --> DB[(MongoDB\nagent_runs)]
    EX --> AUDIT[audit_service.py\nrecord_event]
    AUDIT --> AUDITDB[(MongoDB\naudit_events)]
```

---

## Full Request Lifecycle

```mermaid
flowchart TD
    Client -->|X-API-Key header| SEC2[resolve_tenant\nsecurity.py]
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

The run lifecycle is split across two processes — the API (submit phase) and the worker (execute phase):

```mermaid
flowchart TD
    subgraph Submit["Submit Phase (API process)"]
        A[RunRequest: task + model] --> B[resolve_tenant]
        B --> C[get_agent: 404 guard]
        C --> RL_CHECK[rate limit check\n429 if exceeded]
        RL_CHECK -- 429 --> Z[Error]
        RL_CHECK --> D[guardrail: check_for_injection]
        D -- 400 --> Z[Error]
        D --> E[Insert pending AgentRun]
        E --> F[Enqueue ARQ job]
        E --> AE1[AuditEvent: created]
        F --> G[202 RunSubmitted]
        E --> CARRIER[otel_propagate.inject\ntrace_carrier dict]
        CARRIER --> F
    end

    subgraph Execute["Execute Phase (worker process)"]
        W1[Worker picks up job] --> W2[status: running\nAuditEvent: started]
        W2 --> EXTRACT[restore OTel parent ctx]
        EXTRACT --> W3[anonymize task]
        W3 --> W4[create_react_agent\nMockLLM + tools]
        W4 -->|tool call| W5[execute tool\nguardrail + anonymize output]
        W5 --> W4
        W4 -->|final answer| W6[check output\nanonymize response]
        W6 --> W7[(MongoDB: persist AgentRun)]
        W7 --> W8[status: completed\nAuditEvent: completed]
        W4 -->|guardrail fail| WF[status: failed\nAuditEvent: failed]
    end

    F -.->|job enqueued| W1
```

### Execute Phase Detail

Safety pipeline within a single tool execution step:

```mermaid
flowchart LR
    TASK[raw task] --> INJ[check_for_injection\nPromptInjectionError → 400]
    INJ --> PII1[anonymize_text task]
    PII1 --> LG[LangGraph step]
    LG --> TOUT[tool output]
    TOUT --> SEC[check_tool_output\ninjection → 400, secret → 500]
    SEC --> PII2[anonymize_text output]
    LG --> FOUT[final response]
    FOUT --> OUTCHK[check_output_content\n→ 500]
    OUTCHK --> PII3[anonymize_text response]
```

---

## Layer Summary

| Layer            | Files                                                 | Responsibility                                                                                                                                                                 |
|------------------|-------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Config**       | `core/config.py`                                      | Load and validate all env vars via Pydantic Settings; `REDIS_URL` validator rejects embedded passwords; `REDIS_URL_SAFE` computed field strips credentials for safe logging    |
| **Logging**      | `core/logging.py`                                     | structlog stdlib bridge — emits JSON (or console) per `LOG_JSON`; `TenantContextFilter` injects `tenant`; `_add_otel_trace_context` injects `trace_id`/`span_id`               |
| **Tracing**      | `core/tracing.py`                                     | OTel `TracerProvider` setup; `configure_tracing(app)` / `shutdown_tracing()` / `get_tracer(name)`; idempotency guard for test isolation                                        |
| **Security**     | `core/security.py`                                    | Validate API key → return tenant_id; set `tenant_ctx`; stash `request.state.tenant_id` for rate limiter; track per-IP failed-auth attempts (brute-force prevention)            |
| **Rate Limiting**| `core/rate_limit.py`                                  | Per-tenant sliding-window limiter via `slowapi`; per-IP auth-failure limiter via `limits.MovingWindowRateLimiter`; Redis backend with in-memory fallback                       |
| **Context**      | `core/context.py`                                     | Per-request `ContextVar` storing tenant alias for structured logging; worker resets it via `token`/`reset()` after each job to prevent tenant bleed                            |
| **App entry**    | `main.py`                                             | Create FastAPI app, register routers, manage DB lifecycle; `/health` DB liveness probe with per-IP rate limit; `CORSMiddleware` + `SecurityHeadersMiddleware` applied globally |
| **API**          | `api/v1/`                                             | HTTP routing, request/response serialisation                                                                                                                                   |
| **Schemas**      | `schemas/`                                            | Pydantic validation for all inputs and outputs                                                                                                                                 |
| **Services**     | `services/`                                           | Business logic, DB queries, agent orchestration                                                                                                                                |
| **Models**       | `models/`                                             | Beanie ODM documents → MongoDB collections                                                                                                                                     |
| **Runner**       | `services/runner/`                                    | LangGraph execution, mock LLM, tools, guardrail                                                                                                                                |
| **PII**          | `services/runner/pii.py`                              | Presidio-based PII detection and anonymization                                                                                                                                 |
| **Audit**        | `services/audit_service.py`, `models/audit.py`        | Append-only `AuditEvent` documents — one per lifecycle transition; fire-and-forget (`record_event` never raises)                                                               |
| **Worker**       | `app/worker.py`                                       | ARQ task function; executes agent runs async; writes `completed`/`failed` status                                                                                               |

---

## Structured Logging

Every log line is emitted as JSON (controlled by `LOG_JSON` in `.env`). The structlog processor chain runs in this order for every stdlib `logging.getLogger(__name__)` call:

```mermaid
flowchart LR
    A[LogRecord] --> B[PositionalArgumentsFormatter\nformat printf args]
    B --> C[add_log_level\nadd logger name]
    C --> D[ExtraAdder\nlift record.tenant → event dict]
    D --> OT[_add_otel_trace_context\ntrace_id + span_id when span active]
    OT --> E[TimeStamper\niso-8601 timestamp]
    E --> F{LOG_JSON?}
    F -- true --> G[JSONRenderer\nmachine-parseable]
    F -- false --> H[ConsoleRenderer\nhuman-readable]
```

Output shape (JSON mode):

```json
{"timestamp":"2026-03-16T09:15:32Z","level":"info","logger":"app.api.v1.agents","tenant":"t:alpha","event":"API: Create agent request: name=Research Bot"}
```

`TenantContextFilter` reads the `tenant_ctx` ContextVar (set by `resolve_tenant` on each request) and writes it onto the `LogRecord` as `record.tenant`. `ExtraAdder` then lifts it into the event dict automatically — no call-site changes required.

---

## Distributed Tracing

Every request produces an OpenTelemetry trace. Spans cross the process boundary between the FastAPI API and the ARQ worker via a **W3C traceparent carrier** serialized into the ARQ job kwargs.

### Span Inventory

| Span name                    | Created in           | Key attributes                                                                              |
|------------------------------|----------------------|---------------------------------------------------------------------------------------------|
| `http.*` (auto)              | `FastAPIInstrumentor`| method, route, status code                                                                  |
| `agent.run`                  | `executor.py`        | `agent.id`, `agent.name`, `run.model`, `tenant.id`, `run.id`, `run.steps`, `run.tool_calls` |
| `agent.graph_invoke`         | `executor.py`        | exception info on failure                                                                   |
| `worker.run_agent_task`      | `worker.py`          | `run.id`, `agent.id`, `tenant.id`                                                           |
| `pymongo.*` (auto)           | `PymongoInstrumentor`| DB command, collection                                                                      |

> **PII invariant**: task text, anonymized task, final response, and tool outputs are never set as span attributes.

### Cross-process Trace Propagation

```mermaid
sequenceDiagram
    participant API as API process
    participant Redis
    participant Worker as Worker process

    API->>API: start agent.run span
    API->>API: otel_propagate.inject(trace_carrier)
    Note over API: trace_carrier = {"traceparent": "00-<trace_id>-<span_id>-01"}
    API->>Redis: enqueue_job(..., trace_carrier=trace_carrier)

    Redis->>Worker: dequeue job kwargs
    Worker->>Worker: otel_propagate.extract(trace_carrier)
    Worker->>Worker: start worker.run_agent_task span (parent = API span)
    Note over Worker: same trace_id — single distributed trace
```

### Log Correlation

`_add_otel_trace_context` is a structlog processor inserted after `ExtraAdder()`. When a log line is emitted inside an active span, it appends `trace_id` (32-char hex) and `span_id` (16-char hex) to the event dict:

```json
{
  "timestamp": "2026-03-16T09:15:32Z",
  "level": "info",
  "logger": "app.services.runner.executor",
  "tenant": "t:alpha",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "event": "Agent run completed: run_id=... steps=2"
}
```

Outside an active span (e.g., startup logs), the processor checks `ctx.is_valid` and silently omits both fields.

### Tracing Configuration

| Env var                        | Default | Effect                                                                       |
|--------------------------------|---------|------------------------------------------------------------------------------|
| `OTEL_ENABLED`                 | `true`  | Master switch — set `false` to disable all OTel                              |
| `OTEL_EXPORTER_OTLP_ENDPOINT`  | `""`    | Empty → `ConsoleSpanExporter`; set URL → `OTLPSpanExporter` (HTTP/protobuf)  |
| `OTEL_SERVICE_NAME`            | `""`    | Empty → falls back to `APP_NAME`                                             |

---

## Rate Limiting

Three rate-limiting strategies are active, each with a different key strategy, powered by `slowapi` and the `limits` library.

### POST /agents/{agent_id}/run — per-tenant

```mermaid
flowchart TD
    A[POST /agents/id/run] --> B[resolve_tenant\nstashes tenant_id on request.state]
    B --> C[slowapi async_wrapper\n_check_request_limit]
    C -->|under limit| D[Endpoint body\n→ 202 Accepted]
    C -->|over limit| E[RateLimitExceeded handler\n→ 429 Too Many Requests]
    E --> F[Retry-After header\nX-RateLimit-* headers]
```

### GET /health — per client IP

```mermaid
flowchart TD
    A2[GET /health] --> C2[slowapi async_wrapper\n_check_request_limit]
    C2 -->|under limit| D2[MongoDB ping\n→ 200 ok / 503 degraded]
    C2 -->|over limit| E2[RateLimitExceeded handler\n→ 429 Too Many Requests]
    E2 --> F2[Retry-After header]
```

`/health` issues a live MongoDB `admin.ping` on every call and is unauthenticated. Without a rate limit an attacker can exhaust DB connections by hammering the endpoint. The limiter uses the client IP as the key (no `tenant_id` on unauthenticated requests) via `_tenant_key`'s fallback path.

**Module-scope router**: the `/health` handler is defined on `_health_router` at module level (not inside `create_app()`). This prevents `@limiter.limit()` from appending a new `Limit` object to `limiter._route_limits` on every `create_app()` call — which would multiply the effective counter and trigger false 429s in tests.

### Authentication failures — per client IP (brute-force prevention)

```mermaid
flowchart TD
    A3[Any authenticated endpoint] --> B3[resolve_tenant\nvalidates X-API-Key]
    B3 -->|valid key| C3[Request proceeds normally]
    B3 -->|invalid key| D3[check_auth_failure_limit\nincrement per-IP counter]
    D3 -->|under limit| E3[401 Unauthorized]
    D3 -->|over limit| F3[429 Too Many Requests\ngeneric detail — no key info leaked]
```

`resolve_tenant` tracks failed key validations per client IP using a `MovingWindowRateLimiter` from the `limits` library. The counter is only incremented on failures — valid requests never affect it. Once the threshold is exceeded the dependency raises `HTTP 429` instead of `401`, preventing indefinite brute-force API key enumeration. The 429 response body contains only a generic message; the bad key and IP are never echoed back to the caller. The full warning (including client IP) is logged server-side at `WARNING` level.

**Enabled flag coupling**: `check_auth_failure_limit` reads `limiter.enabled` (the `slowapi` Limiter attribute) so that test fixtures can toggle both limiters with a single attribute write.

### Key Design Decisions

- **Key function** (`_tenant_key`): reads `request.state.tenant_id` set by `resolve_tenant`. Falls back to client IP if the attribute is absent — this fallback is intentionally used by the health endpoint. Each tenant has an independent counter — exhausting one tenant's quota never affects others.
- **Auth failures keyed by IP**: an attacker attempting brute force doesn't have a valid tenant_id yet; `request.client.host` is the only available discriminator.
- **Decorator order** (`@router.post` above `@limiter.limit`): Python applies decorators bottom-up. `@limiter.limit` wraps the function first, then `@router.post` registers the wrapper as the FastAPI route handler. Reversing the order causes FastAPI to register the original (unwrapped) function, silently bypassing all rate limit checks.
- **`response: Response` parameter**: `slowapi` injects `X-RateLimit-*` headers by calling `_inject_headers(kwargs["response"], ...)`. Endpoints that return Pydantic models (not a `starlette.responses.Response`) must declare `response: Response` in their signature — FastAPI injects the live response object, which `slowapi` then mutates to add headers.
- **`app.state.limiter` in `create_app()`**: the `RateLimitExceeded` handler reads `request.app.state.limiter` to build the 429 body. Setting this in the synchronous `create_app()` function (not in the async lifespan) ensures it is available from the very first request, even in tests that skip the lifespan context.

### Rate Limiting Configuration

| Env var                      | Default      | Scope                              | Key                                                  |
|------------------------------|--------------|------------------------------------|------------------------------------------------------|
| `RATE_LIMIT_ENABLED`         | `true`       | all limiters                       | master switch — set `false` to disable all limiting  |
| `RATE_LIMIT_RUN_ENDPOINT`    | `60/minute`  | `POST /agents/{id}/run`            | tenant_id                                            |
| `RATE_LIMIT_HEALTH_ENDPOINT` | `10/minute`  | `GET /health`                      | client IP                                            |
| `RATE_LIMIT_AUTH_FAILURES`   | `10/minute`  | any endpoint (401 path)            | client IP                                            |

### Storage

| Environment  | Backend                                       | Notes                                                                                                                            |
|--------------|-----------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| Production   | Redis (`REDIS_URL`)                           | Shared counters across multiple API instances                                                                                    |
| Redis down   | In-memory (`in_memory_fallback_enabled=True`) | Per-process counters; degraded but functional                                                                                    |
| Tests        | In-memory (`memory://`)                       | `TESTING=True` → `storage_uri="memory://"`; `rl_client` fixture calls `_storage.reset()` for per-test isolation                  |

---

## CORS Policy and Security Response Headers

Two Starlette middlewares are registered globally in `create_app()` — they wrap every response, including errors and preflight requests.

### Middleware Stack Order

Starlette processes middleware in **LIFO order** (last added = outermost). The registration order in `create_app()` is:

1. `app.add_middleware(CORSMiddleware, ...)` — added first
2. `app.add_middleware(SecurityHeadersMiddleware)` — added last (outermost)

This means requests flow: `SecurityHeadersMiddleware` → `CORSMiddleware` → route handler. Security headers are therefore appended to _every_ response, even CORS preflight 4xx or rejected-origin responses.

### CORSMiddleware

Configures the browser Same-Origin Policy for cross-origin API calls.

| Parameter           | Value                                | Notes                                                                                |
|---------------------|--------------------------------------|--------------------------------------------------------------------------------------|
| `allow_origins`     | `settings.CORS_ALLOWED_ORIGINS`      | Default `["*"]` (dev); restrict to specific origins in production                    |
| `allow_credentials` | `False`                              | Cookies and auth headers not allowed cross-origin; API uses `X-API-Key` per-request  |
| `allow_methods`     | `GET, POST, PATCH, DELETE`           | Only methods the API actually exposes                                                |
| `allow_headers`     | `X-API-Key, Content-Type`            | Minimum required headers                                                             |

Set `CORS_ALLOWED_ORIGINS=https://app.example.com,https://admin.example.com` in `.env` to lock down origins in production.

### SecurityHeadersMiddleware

A thin `BaseHTTPMiddleware` that appends four hardening headers to every response:

| Header                       | Value                                 | Protection                                                                                                      |
|------------------------------|---------------------------------------|-----------------------------------------------------------------------------------------------------------------|
| `X-Content-Type-Options`     | `nosniff`                             | Prevents MIME-type sniffing — browser must use the declared `Content-Type`                                      |
| `X-Frame-Options`            | `DENY`                                | Blocks clickjacking — disallows embedding the API in any iframe                                                 |
| `Strict-Transport-Security`  | `max-age=31536000; includeSubDomains` | HSTS — instructs browsers to use HTTPS for 1 year, including all subdomains                                     |
| `X-XSS-Protection`           | `0`                                   | Disables the legacy browser XSS filter (modern browsers use CSP; the old filter can introduce vulnerabilities)  |

### CORS Configuration

| Env var                | Default   | Effect                                                                           |
|------------------------|-----------|----------------------------------------------------------------------------------|
| `CORS_ALLOWED_ORIGINS` | `["*"]`   | Comma-separated allowed origins; `"*"` permits all (development only)            |

---

## Redis URL Credential Safety

`REDIS_URL` is validated by a Pydantic `@field_validator` at Settings construction time:

- **Password rejection**: if `REDIS_URL` contains an embedded password (e.g. `redis://user:secret@host`), `Settings()` raises a `ValidationError` immediately at startup — the app will not start with credentials baked into a URL that could appear in tracebacks or error logs.
- **Safe logging form**: `settings.REDIS_URL_SAFE` is a `@computed_field` that returns `scheme://host:port` with all credential components stripped. Log lines in `worker.py` and anywhere else the connection target is mentioned use `REDIS_URL_SAFE` instead of the raw URL.

```python
# Example
REDIS_URL = "redis://redis-host:6379/0"
REDIS_URL_SAFE → "redis://redis-host:6379"

REDIS_URL = "redis://user:secret@redis-host:6379"   # → ValidationError at startup
```
