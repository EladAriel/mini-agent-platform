"""Tests for REDIS_URL credential masking (M3).

Verifies that:
- REDIS_URL_SAFE strips credentials from any Redis URL
- Pydantic validator rejects URLs containing a password
- Valid plain-URL forms are accepted unchanged
"""

import pytest
from pydantic import ValidationError

from app.core.config import Settings

# Minimal kwargs required to construct a Settings instance without a .env file
_BASE = dict(
    MONGODB_APP_PASSWORD="secret",
    MONGODB_DB="testdb",
    MONGODB_HOST="localhost",
    MAX_EXECUTION_STEPS=10,
    TENANT_API_KEYS={"sk-test": "tenant_alpha"},
)


def _settings(**overrides) -> Settings:
    """Build a Settings instance with REDIS_URL overridden."""
    return Settings(**{**_BASE, **overrides})


class TestRedisUrlSafe:
    """REDIS_URL_SAFE returns only scheme://host:port — no credentials."""

    def test_plain_url_unchanged(self):
        s = _settings(REDIS_URL="redis://localhost:6379")
        assert s.REDIS_URL_SAFE == "redis://localhost:6379"

    def test_url_without_port(self):
        s = _settings(REDIS_URL="redis://redis-host")
        assert s.REDIS_URL_SAFE == "redis://redis-host"

    def test_url_with_username_only_stripped(self):
        # URL has username but no password (RFC-valid; not rejected by validator)
        s = _settings(REDIS_URL="redis://myuser@redis-host:6380")
        # Host:port preserved, username stripped
        assert s.REDIS_URL_SAFE == "redis://redis-host:6380"
        assert "myuser" not in s.REDIS_URL_SAFE

    def test_url_with_path_ignored(self):
        # /0 is a Redis database index — safe form omits it
        s = _settings(REDIS_URL="redis://redis-host:6379/0")
        assert s.REDIS_URL_SAFE == "redis://redis-host:6379"

    def test_safe_url_never_contains_credentials(self):
        # No password means no rejection — but safe form must strip username anyway
        s = _settings(REDIS_URL="redis://justuser@myredis:6379")
        assert "@" not in s.REDIS_URL_SAFE
        assert "justuser" not in s.REDIS_URL_SAFE


class TestRedisUrlPasswordRejected:
    """REDIS_URL with an embedded password must raise a ValidationError at startup."""

    def test_password_in_url_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            _settings(REDIS_URL="redis://user:secretpass@redis-host:6379")
        errors = exc_info.value.errors()
        assert any("REDIS_URL" in str(e) or "password" in str(e).lower() for e in errors)

    def test_error_message_is_descriptive(self):
        with pytest.raises(ValidationError) as exc_info:
            _settings(REDIS_URL="redis://admin:hunter2@redis-host:6379")
        error_str = str(exc_info.value)
        assert "password" in error_str.lower()

    def test_plain_url_no_password_accepted(self):
        """Sanity check: a plain URL without password must NOT raise."""
        s = _settings(REDIS_URL="redis://redis-host:6379")
        assert s.REDIS_URL == "redis://redis-host:6379"
