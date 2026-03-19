"""API-key authentication and tenant resolution."""

from fastapi import Header, HTTPException, Request, status
from app.core.config import settings
from app.core.context import tenant_ctx
from app.core.logging import get_logger
from app.core.rate_limit import check_auth_failure_limit

logger = get_logger(__name__)

def resolve_tenant(
        request: Request,
        x_api_key: str | None = Header(None, alias="X-API-key"),
) -> str:
    """
    FastAPI dependency: Acts as a security gatekeeper for multi-tenancy.

    Why this logic:
    - Extraction: Automatically pulls the 'X-API-key' from the request headers.
    - Validation: Checks the key against the trusted '.env' map. If invalid,
      it halts the request with a 401 Unauthorized to protect system resources.
    - Isolation: Returns the 'tenant_id' so that every subsequent database
      query is strictly scoped to that specific user's data.
    - Auth-failure rate limiting: tracks failed attempts per client IP.
      After RATE_LIMIT_AUTH_FAILURES threshold the caller receives 429
      instead of 401 to prevent indefinite brute-force key scanning.
    """
    tenant_id = settings.TENANT_API_KEYS.get(x_api_key)

    if not tenant_id:
        client_ip = request.client.host if request.client else "unknown"
        if check_auth_failure_limit(client_ip):
            logger.warning("Auth brute-force limit exceeded: ip=%s", client_ip)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed authentication attempts. Try again later.",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )

    # Set a short alias for structured logging: "tenant_alpha" → "t:alpha"
    parts = tenant_id.split("_", 1)
    alias = f"t:{parts[1]}" if len(parts) == 2 else f"t:{tenant_id}"
    tenant_ctx.set(alias)
    request.state.tenant_id = tenant_id   # used by rate limiter key_func
    return tenant_id