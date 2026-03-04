"""
report_plugin.py — pytest plugin that collects structured test data.

Loaded by run_report.py via pytest.main(plugins=[ReportPlugin()]).

For each test it captures:
  - functionality   : the test class name, or "module-level" for bare functions
  - test_name       : human-readable function name (underscores → spaces)
  - status          : PASSED / FAILED / SKIPPED
  - input           : from docstring "Input: ..." line, or positional fallback
  - expected_output : from docstring "Expected: ..." line, or positional fallback
  - actual_output   : assertion error on failure, "✓ assertions passed" on success
  - duration_ms     : wall-clock time for the test body
  - file            : test module path (relative to project root)

Docstring convention (optional — tests without one still appear in the report):
    async def test_create_returns_201(self, client):
        \"\"\"
        Input:    POST /api/v1/tools  body={name, description}
        Expected: 201 with id/name/created_at/updated_at in body
        \"\"\"
"""

from __future__ import annotations

import re
import textwrap
import time
from typing import Any

import pytest


# ── Docstring parsing ─────────────────────────────────────────────────────────

_INPUT_RE    = re.compile(r"^\s*input\s*:\s*(.+)$",    re.I | re.M)
_EXPECTED_RE = re.compile(r"^\s*expected\s*:\s*(.+)$", re.I | re.M)


def _parse_docstring(doc: str | None) -> tuple[str, str]:
    """
    Extract (input, expected) from a test docstring.

    Labelled format (preferred):
        Input:    POST /api/v1/tools  body={name, description}
        Expected: 201 with id/name in response

    Positional fallback — first non-empty line → input,
                          second non-empty line → expected.
    """
    if not doc:
        return "", ""

    cleaned = textwrap.dedent(doc).strip()

    m_in  = _INPUT_RE.search(cleaned)
    m_exp = _EXPECTED_RE.search(cleaned)

    if m_in or m_exp:
        return (
            m_in.group(1).strip()  if m_in  else "",
            m_exp.group(1).strip() if m_exp else "",
        )

    lines = [ln.strip() for ln in cleaned.splitlines() if ln.strip()]
    return (
        lines[0] if len(lines) > 0 else "",
        lines[1] if len(lines) > 1 else "",
    )


# ── Plugin ────────────────────────────────────────────────────────────────────

class ReportPlugin:
    """Attaches to pytest and accumulates one record dict per test."""

    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []
        self._start:  dict[str, float]     = {}

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_protocol(self, item, nextitem):
        self._start[item.nodeid] = time.perf_counter()
        yield

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report  = outcome.get_result()

        if report.when != "call":
            return

        duration_ms = round(
            (time.perf_counter() - self._start.get(item.nodeid, 0)) * 1000, 1
        )

        cls_name   = item.cls.__name__ if item.cls else "module-level"
        human_name = item.originalname.removeprefix("test_").replace("_", " ")
        input_val, expected_val = _parse_docstring(item.function.__doc__)

        if report.passed:
            status        = "PASSED"
            actual_output = _extract_stdout(report) or "✓ assertions passed"
        elif report.failed:
            status        = "FAILED"
            actual_output = _format_failure(report)
        else:
            status        = "SKIPPED"
            actual_output = str(report.longrepr) if report.longrepr else ""

        self.records.append({
            "functionality":   cls_name,
            "test_name":       human_name,
            "status":          status,
            "input":           input_val,
            "expected_output": expected_val,
            "actual_output":   actual_output,
            "duration_ms":     duration_ms,
            "file":            str(item.fspath.relto(item.config.rootdir)),
            "nodeid":          item.nodeid,
        })


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_stdout(report) -> str:
    for name, content in report.sections:
        if "stdout" in name.lower():
            return content.strip()[:300]
    return ""


def _format_failure(report) -> str:
    if report.longrepr is None:
        return "unknown failure"
    text = str(report.longrepr)
    for line in reversed(text.splitlines()):
        line = line.strip()
        if line.startswith(("AssertionError", "assert ", "E ")):
            return line.lstrip("E").strip()[:400]
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return lines[-1][:400] if lines else text[:400]