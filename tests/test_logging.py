"""Tests for structured JSON logging (structlog stdlib bridge)."""

import io
import json
import logging
import sys
from unittest.mock import patch

import pytest

from app.core import logging as logging_module
from app.core.context import tenant_ctx
from app.core.logging import TenantContextFilter, config_logging, get_logger


class TestTenantContextFilter:
    def test_filter_sets_tenant_field(self):
        token = tenant_ctx.set("t:filtertest")
        try:
            record = logging.LogRecord(
                name="test", level=logging.INFO, pathname="", lineno=0,
                msg="msg", args=(), exc_info=None,
            )
            f = TenantContextFilter()
            assert f.filter(record) is True
            assert record.tenant == "t:filtertest"
        finally:
            tenant_ctx.reset(token)

    def test_filter_default_tenant(self):
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="msg", args=(), exc_info=None,
        )
        TenantContextFilter().filter(record)
        assert record.tenant == "-"


class TestConfigLogging:
    def test_config_logging_does_not_raise(self):
        """Smoke test: config_logging() runs without exceptions."""
        config_logging()

    def test_get_logger_returns_stdlib_logger(self):
        logger = get_logger("some.module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "some.module"

    def test_json_output_contains_required_fields(self):
        """Capture stdout, parse JSON line, assert required fields present."""
        buf = io.StringIO()
        with patch.object(sys, "stdout", buf):
            with patch.object(logging_module.settings, "LOG_JSON", True):
                config_logging()
                get_logger("test.json").info("hello %s", "world")

        output = buf.getvalue().strip()
        # Take the last non-empty line in case config_logging itself emits lines
        lines = [l for l in output.splitlines() if l.strip()]
        assert lines, "No log output captured"
        last_line = lines[-1]
        data = json.loads(last_line)

        assert "event" in data
        assert data["event"] == "hello world"
        assert "level" in data
        assert data["level"] == "info"
        assert "timestamp" in data
        assert "logger" in data

    def test_tenant_field_present_in_log_output(self):
        """Set tenant_ctx, capture JSON log, assert tenant key matches."""
        buf = io.StringIO()
        token = tenant_ctx.set("t:plantest")
        try:
            with patch.object(sys, "stdout", buf):
                with patch.object(logging_module.settings, "LOG_JSON", True):
                    config_logging()
                    get_logger("test.tenant").info("tenant check")
        finally:
            tenant_ctx.reset(token)

        output = buf.getvalue().strip()
        lines = [l for l in output.splitlines() if l.strip()]
        assert lines, "No log output captured"
        last_line = lines[-1]
        data = json.loads(last_line)

        assert data.get("tenant") == "t:plantest"
