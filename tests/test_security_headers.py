"""
Tests for M5 — CORS policy and security response headers.

Verifies:
- Security headers (X-Content-Type-Options, X-Frame-Options, HSTS, X-XSS-Protection)
  are present on every response regardless of endpoint or status code.
- CORS: allowed origin gets Access-Control-Allow-Origin echoed back.
- CORS: disallowed origin does NOT get Access-Control-Allow-Origin.
- CORS preflight (OPTIONS) also receives security headers.
- CORS_ALLOWED_ORIGINS="*" reflects the wildcard correctly.
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from tests.conftest import ALPHA


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _assert_security_headers(response):
    """Assert all four security hardening headers are present."""
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "DENY"
    hsts = response.headers.get("strict-transport-security", "")
    assert "max-age=31536000" in hsts
    assert "includeSubDomains" in hsts
    assert response.headers.get("x-xss-protection") == "0"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def sec_client(isolated_db):
    """Standard test client — relies on default CORS_ALLOWED_ORIGINS=["*"]."""
    from app.main import create_app

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        from tests.conftest import FakeArqPool
        app.state.arq_pool = FakeArqPool()
        yield c


# ---------------------------------------------------------------------------
# Security headers — present on every status code
# ---------------------------------------------------------------------------

class TestSecurityHeaders:
    async def test_headers_on_200(self, sec_client):
        """Security headers present on a successful 200 response."""
        r = await sec_client.get("/health")
        assert r.status_code == 200
        _assert_security_headers(r)

    async def test_headers_on_401(self, sec_client):
        """Security headers present even on unauthenticated 401 responses."""
        r = await sec_client.get("/api/v1/agents", headers={"X-API-Key": "bad-key"})
        assert r.status_code == 401
        _assert_security_headers(r)

    async def test_headers_on_404(self, sec_client):
        """Security headers present on 404 responses."""
        r = await sec_client.get(
            "/api/v1/agents/000000000000000000000001",
            headers=ALPHA,
        )
        assert r.status_code == 404
        _assert_security_headers(r)

    async def test_x_content_type_options_value(self, sec_client):
        """X-Content-Type-Options must be exactly 'nosniff'."""
        r = await sec_client.get("/health")
        assert r.headers["x-content-type-options"] == "nosniff"

    async def test_x_frame_options_value(self, sec_client):
        """X-Frame-Options must be exactly 'DENY'."""
        r = await sec_client.get("/health")
        assert r.headers["x-frame-options"] == "DENY"

    async def test_hsts_max_age(self, sec_client):
        """HSTS header must include max-age of 1 year and includeSubDomains."""
        r = await sec_client.get("/health")
        hsts = r.headers["strict-transport-security"]
        assert "max-age=31536000" in hsts
        assert "includeSubDomains" in hsts

    async def test_xss_protection_disabled(self, sec_client):
        """X-XSS-Protection must be '0' (disables the legacy filter)."""
        r = await sec_client.get("/health")
        assert r.headers["x-xss-protection"] == "0"


# ---------------------------------------------------------------------------
# CORS — wildcard default
# ---------------------------------------------------------------------------

class TestCORSWildcard:
    async def test_cors_origin_echoed_for_any_origin(self, sec_client):
        """With CORS_ALLOWED_ORIGINS=["*"], any Origin header is echoed back."""
        r = await sec_client.get(
            "/health",
            headers={"Origin": "https://attacker.example.com"},
        )
        # Starlette CORSMiddleware returns "*" for wildcard config
        assert r.headers.get("access-control-allow-origin") == "*"

    async def test_cors_preflight_returns_security_headers(self, sec_client):
        """CORS preflight OPTIONS also receives security headers."""
        r = await sec_client.options(
            "/api/v1/agents",
            headers={
                "Origin": "https://frontend.example.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "X-API-Key, Content-Type",
            },
        )
        # Preflight should be accepted (2xx) or at worst 400 — not 5xx
        assert r.status_code < 500
        _assert_security_headers(r)


# ---------------------------------------------------------------------------
# CORS — restricted origins
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def restricted_cors_client(isolated_db, monkeypatch):
    """Client with CORS restricted to a single explicit origin."""
    import app.core.config as _cfg_module

    original = _cfg_module.settings.CORS_ALLOWED_ORIGINS
    _cfg_module.settings.CORS_ALLOWED_ORIGINS = ["https://allowed.example.com"]

    from app.main import create_app
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        from tests.conftest import FakeArqPool
        app.state.arq_pool = FakeArqPool()
        yield c

    _cfg_module.settings.CORS_ALLOWED_ORIGINS = original


class TestCORSRestrictedOrigins:
    async def test_allowed_origin_gets_header(self, restricted_cors_client):
        """Allowed origin receives Access-Control-Allow-Origin in response."""
        r = await restricted_cors_client.get(
            "/health",
            headers={"Origin": "https://allowed.example.com"},
        )
        assert r.headers.get("access-control-allow-origin") == "https://allowed.example.com"

    async def test_disallowed_origin_no_acao_header(self, restricted_cors_client):
        """Disallowed origin does NOT receive Access-Control-Allow-Origin."""
        r = await restricted_cors_client.get(
            "/health",
            headers={"Origin": "https://evil.example.com"},
        )
        assert "access-control-allow-origin" not in r.headers

    async def test_security_headers_present_for_disallowed_origin(self, restricted_cors_client):
        """Security hardening headers are present even when CORS rejects the origin."""
        r = await restricted_cors_client.get(
            "/health",
            headers={"Origin": "https://evil.example.com"},
        )
        _assert_security_headers(r)
