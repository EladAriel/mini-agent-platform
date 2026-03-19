"""OpenTelemetry TracerProvider setup."""

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SimpleSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor

from app.core.config import settings

_provider: TracerProvider | None = None


def configure_tracing(app=None) -> None:
    """Initialise the global TracerProvider.

    Idempotent — if `_provider` is already set (e.g. pre-set by a test fixture),
    the function returns immediately without overwriting it.
    """
    global _provider
    if _provider is not None:
        return

    service_name = settings.OTEL_SERVICE_NAME or settings.APP_NAME
    resource = Resource.create({
        SERVICE_NAME: service_name,
        SERVICE_VERSION: "1.0.0",
    })
    _provider = TracerProvider(resource=resource)

    if settings.OTEL_EXPORTER_OTLP_ENDPOINT:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        _provider.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT)
            )
        )
    else:
        _provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(_provider)
    PymongoInstrumentor().instrument()

    if app is not None:
        FastAPIInstrumentor.instrument_app(app)


def shutdown_tracing() -> None:
    """Flush pending spans and tear down the provider."""
    global _provider
    if _provider is not None:
        _provider.shutdown()
        _provider = None


def get_tracer(name: str):
    """Return a tracer scoped to `name` (typically `__name__`)."""
    return trace.get_tracer(name)
