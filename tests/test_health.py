"""
Tests for the /health endpoint — DB liveness probe + rate limiting.

Happy path  : real container DB is reachable → 200 + status ok
Sad path    : broken client (unreachable host) → 503 + status degraded
Sad path    : _client is None (not initialised) → 503 + status degraded
Rate limit  : 3rd request within window → 429 (limit = 2/minute in .env.test)
"""

import pytest
import pytest_asyncio
from pymongo import AsyncMongoClient

import app.core.rate_limit as rl_module
import app.db.db as _db_module


# ---------------------------------------------------------------------------
# Fixture: rate-limit-enabled client (mirrors test_rate_limit.py pattern)
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def rl_client(client):
    """Enable rate limiting and reset storage for health endpoint tests."""
    original_enabled = rl_module.limiter.enabled
    rl_module.limiter.enabled = True
    rl_module.limiter._storage.reset()
    yield client
    rl_module.limiter.enabled = original_enabled


# ---------------------------------------------------------------------------
# Happy path — real MongoDB container is available via isolated_db fixture
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_returns_200_ok(client):
    resp = await client.get("/health")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_body_status_ok(client):
    resp = await client.get("/health")
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_body_db_ok(client):
    resp = await client.get("/health")
    assert resp.json()["checks"]["db"] == "ok"


# ---------------------------------------------------------------------------
# Sad path — broken client (unreachable host)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_returns_503_when_db_down(client):
    original = _db_module._client
    try:
        _db_module._client = AsyncMongoClient(
            "mongodb://localhost:1", serverSelectionTimeoutMS=100
        )
        resp = await client.get("/health")
        assert resp.status_code == 503
    finally:
        _db_module._client = original


@pytest.mark.asyncio
async def test_body_status_degraded_when_db_down(client):
    original = _db_module._client
    try:
        _db_module._client = AsyncMongoClient(
            "mongodb://localhost:1", serverSelectionTimeoutMS=100
        )
        resp = await client.get("/health")
        assert resp.json()["status"] == "degraded"
    finally:
        _db_module._client = original


@pytest.mark.asyncio
async def test_body_db_unavailable_when_db_down(client):
    original = _db_module._client
    try:
        _db_module._client = AsyncMongoClient(
            "mongodb://localhost:1", serverSelectionTimeoutMS=100
        )
        resp = await client.get("/health")
        assert resp.json()["checks"]["db"] == "unavailable"
    finally:
        _db_module._client = original


# ---------------------------------------------------------------------------
# Sad path — _client is None (not yet initialised)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_returns_503_when_client_is_none(client):
    original = _db_module._client
    try:
        _db_module._client = None
        resp = await client.get("/health")
        assert resp.status_code == 503
    finally:
        _db_module._client = original


# ---------------------------------------------------------------------------
# Rate limiting — /health is unauthenticated; keyed by client IP
# RATE_LIMIT_HEALTH_ENDPOINT=2/minute in .env.test  →  3rd call → 429
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_health_within_limit_returns_200(rl_client):
    """First two requests (within the 2/min limit) must succeed."""
    for _ in range(2):
        resp = await rl_client.get("/health")
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_health_exceeding_limit_returns_429(rl_client):
    """Third request within the same minute must be rejected with 429."""
    for _ in range(2):
        r = await rl_client.get("/health")
        assert r.status_code == 200

    r = await rl_client.get("/health")
    assert r.status_code == 429


@pytest.mark.asyncio
async def test_health_429_has_retry_after_header(rl_client):
    """HTTP 429 on /health must include a Retry-After header."""
    for _ in range(2):
        await rl_client.get("/health")

    r = await rl_client.get("/health")
    assert r.status_code == 429
    assert "retry-after" in r.headers
