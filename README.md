# Mini Agent Platform

A multi-tenant REST API for managing AI agents, registering tools, and running traceable task executions — built with FastAPI, MongoDB, and LangGraph.

---

## What It Does

- **Manage Tools** — Register reusable capabilities (web search, calculator, weather, etc.)
- **Manage Agents** — Create AI agents with a name, role, description, and assigned tools
- **Run Agents** — Submit an agent run (202 async); poll `GET /runs/{run_id}` until `completed` or `failed`
- **View History** — Browse paginated run history per-agent or across all agents
- **Multi-Tenancy** — Every resource is strictly scoped to a tenant via API key
- **Rate Limiting** — Sliding-window per-tenant throttle on run submissions; per-IP throttle on `GET /health` (prevents DB connection exhaustion); returns HTTP 429 with `Retry-After` and `X-RateLimit-*` headers on violation
- **Security Guardrails** — Prompt injection and credential leak detection; PII anonymized before storage
- **Structured JSON Logging** — Every log line emitted as machine-parseable JSON with `timestamp`, `level`, `logger`, `tenant`, and `event` fields; compatible with Datadog, ELK, and any log aggregator
- **Immutable Audit Log** — Every run lifecycle transition (created → started → completed/failed) is written as an append-only `AuditEvent` document for compliance and traceability
- **Distributed Tracing** — Every request carries an OpenTelemetry trace. Spans cover the full path: HTTP handler → worker task → LangGraph invocation. `trace_id` and `span_id` are automatically injected into every JSON log line.

---

## Requirements

- [Docker](https://www.docker.com/) + Docker Compose
- No Python installation needed to run the app

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/EladAriel/mini-agent-platform.git
cd mini-agent-platform
```

### 2. Create your `.env` file

Copy `.env.example`:

```bash
cp .env.example .env
```

Edit `.env`.

> **`TENANT_API_KEYS`** is a JSON object mapping API keys to tenant IDs. Add as many tenants as you need.
>
> **`REDIS_URL`** is the connection string for the Redis instance used by the ARQ worker (default: `redis://localhost:6379`).
>
> **`RATE_LIMIT_ENABLED`** enables per-tenant rate limiting (default: `true`).
> **`RATE_LIMIT_RUN_ENDPOINT`** sets the limit string (default: `60/minute`). Limits are keyed by tenant — exhausting one tenant's quota never affects others.
> **`RATE_LIMIT_HEALTH_ENDPOINT`** caps unauthenticated health checks by client IP (default: `10/minute`) to protect MongoDB from connection exhaustion.
>
> **`LOG_JSON`** controls log format: `true` emits machine-parseable JSON (default); `false` emits human-readable console output (useful during development).
>
> **`OTEL_ENABLED`** enables distributed tracing (default: `true`). Set `OTEL_EXPORTER_OTLP_ENDPOINT` to a collector URL (e.g., `http://otel-collector:4318`) to export spans; leave it empty to print spans to stdout.

### 3. Start the app

```bash
docker compose up --build
```

The API will be available at **<http://localhost:8000>**

Interactive docs at **<http://localhost:8000/docs>**

> **Tip:** Run services in separate terminals for cleaner logs.

```bash
# Terminal 1
docker compose up mongo redis

# Terminal 2
docker compose up worker --build

# Terminal 3
docker compose up api --build        # production
docker compose up api-dev --build    # development (hot reload)
```

### Teardown

```bash
docker compose down -v    # stops containers and removes the mongo_data volume
```

---

## Running Tests

Tests use a real MongoDB container via Testcontainers — Docker must be running.

Create a `.env.test` file:

```env
MONGODB_APP_PASSWORD=test
MONGODB_DB=test_db
MONGODB_HOST=localhost
MAX_EXECUTION_STEPS=10
TENANT_API_KEYS={"sk-tenant-alpha-000": "tenant_alpha", "sk-tenant-beta-000": "tenant_beta"}
TESTING=true
LOG_JSON=false
```

```bash
pip install -r requirements.txt
pytest
```

Or generate an HTML report:

```bash
python tests/create_test_report/run_report.py --open

# Also save the intermediate .md file (useful for git diffs)
python tests/create_test_report/run_report.py --md --open
```

---

## Worker (Async Execution)

Agent runs are executed by a separate ARQ worker process backed by Redis. When running via Docker Compose, the `worker` service starts automatically alongside `api` — no extra steps needed.

> Without the worker running, submitted runs will remain in `pending` status indefinitely.

To run the worker manually (outside Docker, for local development):

```bash
# Redis must be running first
arq app.worker.WorkerSettings
```

---

## Development Mode

```bash
docker compose --profile dev up api-dev --build
```

## Health Check

```bash
curl http://localhost:8000/health
# {"status":"ok","checks":{"db":"ok"}}

# When MongoDB is unreachable:
# HTTP 503 {"status":"degraded","checks":{"db":"unavailable"}}

# When rate limit is exceeded (default: 10/minute per client IP):
# HTTP 429 Too Many Requests
```

> The `/health` endpoint is rate-limited by client IP (`RATE_LIMIT_HEALTH_ENDPOINT`, default `10/minute`). This prevents unauthenticated callers from hammering the live MongoDB ping and exhausting DB connections.

---

## Documentation

| Doc | Description |
| --- | ----------- |
| [architecture.md](docs/architecture.md) | System overview, Docker setup, request lifecycle |
| [api.md](docs/api.md) | All endpoints, request/response flow, error codes |
| [services.md](docs/services.md) | Business logic, executor, guardrail, mock LLM |
| [models_schemas_db.md](docs/models_schemas_db.md) | MongoDB models, Pydantic schemas, indexes |
| [quickstart_testing.md](docs/quickstart_testing.md) | Step-by-step Swagger UI testing guide |
| [bug_fixing_demo.ipynb](examples/bug_fixing_demo.ipynb) | End-to-end walkthrough: tools, agents, runs, guardrails, PII, multi-tenancy, audit log |
