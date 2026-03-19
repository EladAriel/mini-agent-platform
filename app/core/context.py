"""Per-request context variables for structured logging."""

from contextvars import ContextVar

# Holds a short tenant alias (e.g. "t:alpha") for the lifetime of each request.
# Default "-" appears in log lines before any tenant is resolved (e.g. startup,
# unauthenticated requests).
tenant_ctx: ContextVar[str] = ContextVar("tenant_ctx", default="-")
