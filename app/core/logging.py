"""Application logging configuration — structlog stdlib bridge."""

import logging
import sys

import structlog

from app.core.config import settings
from app.core.context import tenant_ctx


class TenantContextFilter(logging.Filter):
    """Injects the current tenant alias into every LogRecord as `tenant`."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.tenant = tenant_ctx.get()
        return True


def _add_otel_trace_context(logger, method, event_dict):
    """Structlog processor: injects trace_id and span_id when inside an active OTel span."""
    try:
        from opentelemetry import trace as otel_trace
        ctx = otel_trace.get_current_span().get_span_context()
        if ctx.is_valid:
            event_dict["trace_id"] = format(ctx.trace_id, "032x")
            event_dict["span_id"]  = format(ctx.span_id,  "016x")
    except ImportError:
        pass
    return event_dict


def _shared_processors() -> list:
    return [
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.ExtraAdder(),
        _add_otel_trace_context,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.format_exc_info,
    ]


def config_logging() -> None:
    """Configure application logging with structlog JSON (or console) output."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    shared = _shared_processors()

    structlog.configure(
        processors=shared + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    if settings.LOG_JSON:
        final_processors = [
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),
        ]
    else:
        final_processors = [
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.dev.ConsoleRenderer(colors=False),
        ]

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared,
        processors=final_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(TenantContextFilter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(log_level)

    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logging.getLogger("beanie").setLevel(logging.WARNING)
    logging.getLogger("arq").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a stdlib logger instance. Signature unchanged."""
    return logging.getLogger(name)
