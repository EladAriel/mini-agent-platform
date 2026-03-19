"""
Tests for per-tenant rate limiting on POST /agents/{agent_id}/run.

Strategy
--------
- .env.test sets RATE_LIMIT_ENABLED=false (no throttling for normal tests)
  and RATE_LIMIT_RUN_ENDPOINT=3/minute (low limit baked at decorator import time).
- `rl_client` fixture enables the limiter and resets in-memory storage so each
  test starts with a fresh counter — no Redis required (in_memory_fallback).
- Rate limit counter is keyed on tenant_id (stashed by resolve_tenant).
"""

import pytest
import pytest_asyncio

import app.core.rate_limit as rl_module
from tests.conftest import ALPHA, BETA

TOOLS_URL  = "/api/v1/tools"
AGENTS_URL = "/api/v1/agents"


# ---------------------------------------------------------------------------
# Helpers (mirror test_agents_runs_api.py)
# ---------------------------------------------------------------------------

async def create_tool(client, *, headers=ALPHA):
    r = await client.post(
        TOOLS_URL,
        json={"name": "web_search", "description": "Searches the web."},
        headers=headers,
    )
    assert r.status_code == 201
    return r.json()["id"]


async def create_agent(client, *, headers=ALPHA):
    r = await client.post(
        AGENTS_URL,
        json={"name": "Researcher", "role": "Research Assistant", "description": "Finds info.", "tool_ids": []},
        headers=headers,
    )
    assert r.status_code == 201
    return r.json()["id"]


async def run_agent(client, agent_id, *, headers=ALPHA):
    return await client.post(
        f"{AGENTS_URL}/{agent_id}/run",
        json={"task": "Simple task.", "model": "gpt-4o"},
        headers=headers,
    )


# ---------------------------------------------------------------------------
# Fixture: rate-limit-enabled client
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def rl_client(client):
    """
    Re-use the standard `client` fixture but enable rate limiting.

    Steps:
    1. Save and override limiter.enabled → True.
    2. Reset the in-memory storage so each test starts with a clean counter.
       In tests, TESTING=True means the limiter uses MemoryStorage directly
       (no Redis), so _storage.reset() clears all keys instantly.
    3. Yield the client.
    4. Restore original enabled state in teardown.
    """
    original_enabled = rl_module.limiter.enabled

    rl_module.limiter.enabled = True
    rl_module.limiter._storage.reset()  # clear all per-tenant counters

    yield client

    rl_module.limiter.enabled = original_enabled


# ---------------------------------------------------------------------------
# Fixtures: agent under ALPHA and BETA tenants
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def alpha_agent_id(rl_client):
    return await create_agent(rl_client, headers=ALPHA)


@pytest_asyncio.fixture
async def beta_agent_id(rl_client):
    return await create_agent(rl_client, headers=BETA)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_below_limit_returns_202(rl_client, alpha_agent_id):
    """First request (well within the 3/min limit) must succeed with 202."""
    r = await run_agent(rl_client, alpha_agent_id)
    assert r.status_code == 202


@pytest.mark.asyncio
async def test_exceeding_limit_returns_429(rl_client, alpha_agent_id):
    """4th request within the same minute must be rejected with 429."""
    for _ in range(3):
        r = await run_agent(rl_client, alpha_agent_id)
        assert r.status_code == 202

    r = await run_agent(rl_client, alpha_agent_id)
    assert r.status_code == 429


@pytest.mark.asyncio
async def test_429_has_retry_after_header(rl_client, alpha_agent_id):
    """HTTP 429 response must include a Retry-After header."""
    for _ in range(3):
        await run_agent(rl_client, alpha_agent_id)

    r = await run_agent(rl_client, alpha_agent_id)
    assert r.status_code == 429
    assert "retry-after" in r.headers


@pytest.mark.asyncio
async def test_429_has_x_ratelimit_headers(rl_client, alpha_agent_id):
    """HTTP 429 response must include X-RateLimit-Limit and X-RateLimit-Remaining."""
    for _ in range(3):
        await run_agent(rl_client, alpha_agent_id)

    r = await run_agent(rl_client, alpha_agent_id)
    assert r.status_code == 429
    assert "x-ratelimit-limit" in r.headers
    assert "x-ratelimit-remaining" in r.headers


@pytest.mark.asyncio
async def test_tenant_isolation(rl_client, alpha_agent_id, beta_agent_id):
    """
    Exhausting ALPHA's quota must NOT block BETA.

    ALPHA submits 4 requests (exceeds limit=3). BETA submits 1 request
    afterwards — should still receive 202.
    """
    for _ in range(3):
        await run_agent(rl_client, alpha_agent_id, headers=ALPHA)

    # ALPHA is now rate-limited
    r = await run_agent(rl_client, alpha_agent_id, headers=ALPHA)
    assert r.status_code == 429

    # BETA is on a separate counter — must still succeed
    r = await run_agent(rl_client, beta_agent_id, headers=BETA)
    assert r.status_code == 202


@pytest.mark.asyncio
async def test_read_endpoints_not_rate_limited(rl_client):
    """
    GET /agents must never return 429 regardless of how many times it's called.

    Rate limiting is applied only to the run submission endpoint.
    """
    for _ in range(10):
        r = await rl_client.get(AGENTS_URL, headers=ALPHA)
        assert r.status_code == 200
