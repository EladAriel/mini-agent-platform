"""Application configuration."""

from urllib.parse import urlparse, urlunparse

from pydantic import computed_field, field_validator
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Mini Agent Platform"

    # Logger
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_JSON: bool = True   # False = human-readable console (dev only)

    # OpenTelemetry tracing
    OTEL_ENABLED: bool = True
    OTEL_EXPORTER_OTLP_ENDPOINT: str = ""   # e.g. "http://otel-collector:4318"; empty = ConsoleSpanExporter
    OTEL_SERVICE_NAME: str = ""             # defaults to APP_NAME at runtime if empty

    # MongoDB setup — FastAPI connects as app_user only
    MONGODB_APP_USER: str = "app_user"
    MONGODB_APP_PASSWORD: str
    MONGODB_DB: str
    MONGODB_HOST: str

    @computed_field
    @property
    def MONGODB_URI(self) -> str:
        url = MultiHostUrl.build(
            scheme="mongodb",
            username=self.MONGODB_APP_USER,
            password=self.MONGODB_APP_PASSWORD,
            host=self.MONGODB_HOST,
            path=self.MONGODB_DB,
            query=f"authSource={self.MONGODB_DB}"
        )
        return str(url)

    MAX_EXECUTION_STEPS: int
    TENANT_API_KEYS: dict[str, str]
    REDIS_URL: str = "redis://localhost:6379"
    TESTING: bool = False

    @field_validator("REDIS_URL")
    @classmethod
    def _reject_redis_credentials(cls, v: str) -> str:
        """Reject Redis URLs that embed a password to prevent accidental credential leaks.

        If a password is present (redis://user:password@host), Settings construction
        fails at startup with a clear error rather than silently accepting a URL whose
        credentials could appear in logs or tracebacks.
        """
        parsed = urlparse(v)
        if parsed.password:
            raise ValueError(
                "REDIS_URL must not contain an embedded password. "
                "Use redis://host:port and configure auth separately."
            )
        return v

    @computed_field
    @property
    def REDIS_URL_SAFE(self) -> str:
        """Redis URL with credentials stripped — safe to log or surface in tracebacks.

        Returns only scheme://host:port (no username, no password, no path/query).
        Example: redis://user:secret@redis-host:6379/0 → redis://redis-host:6379
        """
        parsed = urlparse(self.REDIS_URL)
        # Reconstruct with netloc reduced to host:port only (no userinfo)
        host_port = parsed.hostname or "localhost"
        if parsed.port:
            host_port = f"{host_port}:{parsed.port}"
        return urlunparse((parsed.scheme, host_port, "", "", "", ""))

    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_RUN_ENDPOINT: str = "60/minute"      # slowapi limit string, configurable per env
    RATE_LIMIT_HEALTH_ENDPOINT: str = "10/minute"   # unauthenticated; keyed by client IP
    RATE_LIMIT_AUTH_FAILURES: str = "10/minute"     # failed auth attempts per IP before 429

    # CORS — comma-separated list of allowed origins; "*" permits all (dev only)
    CORS_ALLOWED_ORIGINS: list[str] = ["*"]

    @field_validator("CORS_ALLOWED_ORIGINS", mode="before")
    @classmethod
    def _parse_cors_origins(cls, v: object) -> object:
        """Accept bare strings (e.g. "*" or "a.com,b.com") as well as JSON arrays.

        pydantic-settings v2 attempts json.loads() on list[str] fields, so a bare
        string like CORS_ALLOWED_ORIGINS=* causes a JSONDecodeError at startup.
        This validator normalises bare strings into a list before pydantic's JSON
        coercion fires.
        """
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                # Looks like a JSON array — let pydantic's default JSON coercion handle it.
                return v
            # Comma-separated or single value (e.g. "*", "https://app.example.com")
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra="ignore",
    )

settings = Settings()