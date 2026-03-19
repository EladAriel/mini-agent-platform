"""Per-tenant rate limiting via slowapi."""

from limits import parse as _parse_limit
from limits.storage import storage_from_string as _storage_from_uri
from limits.strategies import MovingWindowRateLimiter as _MovingWindowRateLimiter
from slowapi import Limiter, _rate_limit_exceeded_handler  # noqa: F401 — re-exported
from slowapi.errors import RateLimitExceeded                # noqa: F401 — re-exported

from app.core.config import settings

# Use in-memory storage during tests so no Redis connection is needed.
# Redis is used in production (TESTING=False).
_storage_uri = "memory://" if settings.TESTING else settings.REDIS_URL


def _tenant_key(request) -> str:
    """Key on tenant_id stashed by resolve_tenant(); falls back to client IP."""
    return getattr(request.state, "tenant_id", request.client.host)


limiter = Limiter(
    key_func=_tenant_key,
    storage_uri=_storage_uri,
    headers_enabled=True,                   # emit X-RateLimit-* + Retry-After headers
    enabled=settings.RATE_LIMIT_ENABLED,    # False in tests via .env.test
    in_memory_fallback_enabled=True,        # degrade gracefully on Redis outage
    key_prefix="rl:run:",                   # namespace to avoid ARQ key collisions
)

# ---------------------------------------------------------------------------
# Auth-failure rate limiter (separate from the endpoint limiter above).
#
# Keyed per client IP.  Only incremented on 401 failures inside resolve_tenant.
# Uses the same storage backend so tests get in-memory and production gets Redis.
# A dedicated storage + strategy object is used instead of @limiter.limit so we
# can call hit() imperatively inside a FastAPI dependency (not a route handler).
# ---------------------------------------------------------------------------
_auth_storage = _storage_from_uri(_storage_uri)
_auth_strategy = _MovingWindowRateLimiter(_auth_storage)
_auth_limit = _parse_limit(settings.RATE_LIMIT_AUTH_FAILURES)


def check_auth_failure_limit(ip: str) -> bool:
    """
    Record a failed auth attempt for *ip* and return True if the IP is now
    over the configured limit, False otherwise.

    Uses the same `limiter.enabled` flag as the endpoint limiter so tests can
    toggle both with a single attribute write (mirrors the rl_client fixture).
    """
    if not limiter.enabled:
        return False
    # hit() increments the counter and returns True while still under the limit.
    # Once the limit is exceeded it returns False — meaning the call is blocked.
    return not _auth_strategy.hit(_auth_limit, "auth_fail", ip)
