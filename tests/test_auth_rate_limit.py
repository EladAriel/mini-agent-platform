"""
Tests for auth-failure rate limiting in resolve_tenant().

Strategy
--------
- .env.test sets RATE_LIMIT_ENABLED=false so normal test suite is unaffected.
- `rl_auth_client` fixture enables the limiter AND resets the auth-failure
  storage (_auth_storage) for per-test counter isolation.
- RATE_LIMIT_AUTH_FAILURES=3/minute in .env.test → 4th bad attempt → 429.
- Valid-key requests must never be affected by failed-auth counters.
"""

import pytest
import pytest_asyncio

import app.core.rate_limit as rl_module
from tests.conftest import ALPHA, BAD

AGENTS_URL = "/api/v1/agents"


# ---------------------------------------------------------------------------
# Fixture: rate-limit-enabled client that also resets auth-failure storage
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def rl_auth_client(client):
    """
    Enable rate limiting for auth-failure tests.

    Resets both the main limiter storage AND the auth-failure storage so
    each test starts with zeroed counters — no cross-test contamination.
    """
    original_enabled = rl_module.limiter.enabled

    rl_module.limiter.enabled = True
    rl_module.limiter._storage.reset()
    rl_module._auth_storage.reset()     # separate counter store for auth failures

    yield client

    rl_module.limiter.enabled = original_enabled


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_bad_key_returns_401(rl_auth_client):
    """First failed attempt must return 401, not 429."""
    r = await rl_auth_client.get(AGENTS_URL, headers=BAD)
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_bad_key_within_limit_returns_401(rl_auth_client):
    """Attempts within the failure threshold must each return 401."""
    for _ in range(3):
        r = await rl_auth_client.get(AGENTS_URL, headers=BAD)
        assert r.status_code == 401


@pytest.mark.asyncio
async def test_exceeding_auth_failure_limit_returns_429(rl_auth_client):
    """4th bad attempt within the window must return 429."""
    for _ in range(3):
        r = await rl_auth_client.get(AGENTS_URL, headers=BAD)
        assert r.status_code == 401

    r = await rl_auth_client.get(AGENTS_URL, headers=BAD)
    assert r.status_code == 429


@pytest.mark.asyncio
async def test_429_detail_is_generic(rl_auth_client):
    """
    The 429 body must not leak any internal information (no key values,
    no pattern matches, no IP address).
    """
    for _ in range(3):
        await rl_auth_client.get(AGENTS_URL, headers=BAD)

    r = await rl_auth_client.get(AGENTS_URL, headers=BAD)
    assert r.status_code == 429
    body = r.json()
    # Must contain the generic user-facing message
    assert "Too many failed authentication attempts" in body["detail"]
    # Must NOT leak the key or IP
    assert "sk-bad-key" not in body["detail"]


@pytest.mark.asyncio
async def test_valid_key_succeeds_after_bad_attempts(rl_auth_client):
    """
    Valid-key requests must succeed even if the same IP exceeded the failed-auth
    threshold. The counter only throttles 401 paths — authenticated requests
    are completely unaffected.
    """
    # Exhaust the failed-auth limit
    for _ in range(4):
        await rl_auth_client.get(AGENTS_URL, headers=BAD)

    # A request with a valid key must still get through
    r = await rl_auth_client.get(AGENTS_URL, headers=ALPHA)
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_auth_failure_limit_disabled_by_default(client):
    """
    When RATE_LIMIT_ENABLED=false (default in .env.test) many bad requests
    must all return 401 — never 429.
    """
    for _ in range(10):
        r = await client.get(AGENTS_URL, headers=BAD)
        assert r.status_code == 401
