"""
Tests for OpenTelemetry distributed tracing.

Uses InMemorySpanExporter so no external collector is needed.
The session-scoped `otel_test_provider` fixture pre-sets _provider before
any lifespan runs, which blocks configure_tracing() from overwriting it
(idempotency guard).
"""
import json
import logging
import pytest
import pytest_asyncio

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry import propagate as otel_propagate

import app.core.tracing as tracing_module
from tests.conftest import ALPHA


# ── Session-scoped provider ────────────────────────────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def otel_test_provider():
    """
    Install an InMemorySpanExporter ONCE for the entire test session.

    Sets tracing_module._provider before any client fixture triggers lifespan,
    so configure_tracing() sees _provider != None and returns immediately —
    the test provider is never replaced.
    """
    exporter = InMemorySpanExporter()
    provider = TracerProvider(resource=Resource.create({SERVICE_NAME: "test"}))
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    tracing_module._provider = provider   # block lifespan from replacing it
    yield exporter
    provider.shutdown()
    tracing_module._provider = None


@pytest.fixture(autouse=True)
def clear_spans(otel_test_provider):
    """Wipe the exporter before each test to prevent cross-test pollution."""
    otel_test_provider.clear()
    yield


# ── Helpers ────────────────────────────────────────────────────────────────────

async def _make_run(client, alpha_headers=ALPHA):
    """Create an agent with a tool and submit a run. Returns the run JSON."""
    # Create a tool
    tool_r = await client.post(
        "/api/v1/tools",
        headers=alpha_headers,
        json={"name": "web_search", "description": "Searches the web"},
    )
    tool_id = tool_r.json()["id"]

    # Create an agent assigned to that tool
    agent_r = await client.post(
        "/api/v1/agents",
        headers=alpha_headers,
        json={
            "name": "Test Agent",
            "role": "Tester",
            "description": "A test agent",
            "tool_ids": [tool_id],
        },
    )
    agent_id = agent_r.json()["id"]

    # Submit a run
    run_r = await client.post(
        f"/api/v1/agents/{agent_id}/run",
        headers=alpha_headers,
        json={"task": "Do something helpful"},
    )
    assert run_r.status_code == 202
    return run_r.json()


def _get_spans_by_name(exporter, name: str):
    return [s for s in exporter.get_finished_spans() if s.name == name]


# ── Tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_run_agent_emits_agent_run_span(client, otel_test_provider):
    """A completed run must produce at least one 'agent.run' span."""
    await _make_run(client)
    spans = _get_spans_by_name(otel_test_provider, "agent.run")
    assert len(spans) == 1


@pytest.mark.asyncio
async def test_agent_run_span_has_agent_id_attribute(client, otel_test_provider):
    """'agent.run' span must carry agent.id and tenant.id attributes."""
    await _make_run(client)
    span = _get_spans_by_name(otel_test_provider, "agent.run")[0]
    assert "agent.id" in span.attributes
    assert span.attributes["tenant.id"] == "tenant_alpha"


@pytest.mark.asyncio
async def test_graph_invoke_span_nested_in_agent_run(client, otel_test_provider):
    """'agent.graph_invoke' parent span_id must equal 'agent.run' span_id."""
    await _make_run(client)
    run_span = _get_spans_by_name(otel_test_provider, "agent.run")[0]
    graph_span = _get_spans_by_name(otel_test_provider, "agent.graph_invoke")[0]
    assert graph_span.parent is not None
    assert graph_span.parent.span_id == run_span.context.span_id


@pytest.mark.asyncio
async def test_run_span_has_steps_attribute(client, otel_test_provider):
    """'agent.run' span must carry run.steps and run.id attributes after execution."""
    await _make_run(client)
    span = _get_spans_by_name(otel_test_provider, "agent.run")[0]
    assert "run.steps" in span.attributes
    assert "run.id" in span.attributes


@pytest.mark.asyncio
async def test_no_pii_in_span_attributes(client, otel_test_provider):
    """Task text must never appear in any span attribute value."""
    task_text = "Do something helpful"
    await _make_run(client)
    all_spans = otel_test_provider.get_finished_spans()
    for span in all_spans:
        for val in span.attributes.values():
            assert task_text not in str(val), (
                f"Task text found in span '{span.name}' attribute: {val}"
            )


@pytest.mark.asyncio
async def test_worker_emits_worker_span(client, otel_test_provider):
    """FakeArqPool runs the worker synchronously — worker span must be captured."""
    await _make_run(client)
    spans = _get_spans_by_name(otel_test_provider, "worker.run_agent_task")
    assert len(spans) == 1


@pytest.mark.asyncio
async def test_worker_span_has_run_and_agent_attributes(client, otel_test_provider):
    """worker.run_agent_task span must carry run.id, agent.id, tenant.id."""
    run_data = await _make_run(client)
    span = _get_spans_by_name(otel_test_provider, "worker.run_agent_task")[0]
    assert span.attributes["run.id"] == run_data["run_id"]
    assert "agent.id" in span.attributes
    assert span.attributes["tenant.id"] == "tenant_alpha"


@pytest.mark.asyncio
async def test_trace_context_propagated_via_carrier(client, otel_test_provider):
    """
    Worker span's trace_id must match the API's agent.run span trace_id.
    This proves the W3C traceparent carrier was injected (agents.py) and
    extracted (worker.py), linking both spans to the same distributed trace.
    """
    await _make_run(client)
    run_span = _get_spans_by_name(otel_test_provider, "agent.run")[0]
    worker_span = _get_spans_by_name(otel_test_provider, "worker.run_agent_task")[0]
    assert run_span.context.trace_id == worker_span.context.trace_id


@pytest.mark.asyncio
async def test_log_contains_trace_id_when_span_active(otel_test_provider, caplog):
    """
    When a log line is emitted inside an active OTel span, the JSON output
    must include a 32-char hex 'trace_id' field.
    """
    from app.core.logging import _add_otel_trace_context

    tracer = trace.get_tracer("test")
    with tracer.start_as_current_span("test.log_span"):
        event_dict = {}
        result = _add_otel_trace_context(None, None, event_dict)
        assert "trace_id" in result
        assert len(result["trace_id"]) == 32
        assert result["trace_id"] != "0" * 32
        assert "span_id" in result
        assert len(result["span_id"]) == 16


def test_log_omits_trace_id_when_no_span_active():
    """Outside any span, _add_otel_trace_context must not inject trace_id."""
    from app.core.logging import _add_otel_trace_context
    event_dict = {}
    result = _add_otel_trace_context(None, None, event_dict)
    assert "trace_id" not in result
    assert "span_id" not in result


def test_configure_tracing_is_idempotent(otel_test_provider):
    """
    Calling configure_tracing() while _provider is already set must be a no-op.
    The test provider installed by otel_test_provider must remain untouched.
    """
    import app.core.tracing as tracing_module
    from app.core.tracing import configure_tracing

    original_provider = tracing_module._provider
    configure_tracing()   # second call — should return immediately
    assert tracing_module._provider is original_provider
