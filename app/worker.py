"""ARQ worker — async task queue backed by Redis.

Launch with:
    arq app.worker.WorkerSettings

The worker process initialises its own Beanie connection via on_startup/on_shutdown
hooks so it is completely independent of the FastAPI app process.
"""
from datetime import datetime, timezone

from fastapi import HTTPException
from arq.connections import RedisSettings as ArqRedisSettings
from opentelemetry import propagate as otel_propagate

from app.core.config import settings
from app.core.context import tenant_ctx
from app.core.logging import config_logging, get_logger
from app.core.tracing import get_tracer
from app.db.db import init_db, close_db
from app.models.run import AgentRun, RUN_STATUS_RUNNING, RUN_STATUS_FAILED
from app.services import agent_service
from app.services.audit_service import record_event
from app.services.runner.executor import run_agent
from app.schemas.run import RunRequest
from app.models.audit import AUDIT_EVENT_STARTED, AUDIT_EVENT_FAILED

config_logging()
logger = get_logger(__name__)
_tracer = get_tracer(__name__)


async def _arq_startup(ctx: dict) -> None:
    """ARQ on_startup hook — wraps init_db() to accept the ctx arg ARQ always passes."""
    await init_db()


async def _arq_shutdown(ctx: dict) -> None:
    """ARQ on_shutdown hook — wraps close_db() to accept the ctx arg ARQ always passes."""
    await close_db()


async def run_agent_task(
    ctx: dict,
    *,
    run_id: str,
    agent_id: str,
    tenant_id: str,
    task: str,
    model: str,
    trace_carrier: dict | None = None,
) -> None:
    """
    ARQ task: execute a queued agent run.

    MUST NOT raise — any exception is caught and stored as status='failed'
    so clients polling GET /runs/{run_id} always reach a terminal state.
    """
    # Set tenant context for structured logging; reset in finally to prevent
    # context bleed between concurrent jobs sharing the same event loop.
    parts = tenant_id.split("_", 1)
    _token = tenant_ctx.set(f"t:{parts[1]}" if len(parts) == 2 else f"t:{tenant_id}")

    try:
        # Restore the distributed trace context propagated from the API process
        parent_ctx = otel_propagate.extract(trace_carrier or {})

        with _tracer.start_as_current_span(
            "worker.run_agent_task",
            context=parent_ctx,
            attributes={"run.id": run_id, "agent.id": agent_id, "tenant.id": tenant_id},
        ):
            logger.info("Worker: starting run_id=%s agent_id=%s", run_id, agent_id)

            # Transition to running
            from beanie import PydanticObjectId
            run = await AgentRun.find_one(AgentRun.id == PydanticObjectId(run_id))
            if run is None:
                logger.error("Worker: run_id=%s not found in DB, aborting", run_id)
                return

            await run.update({"$set": {
                "status": RUN_STATUS_RUNNING,
                "started_at": datetime.now(timezone.utc),
            }})

            await record_event(run_id=run_id, tenant_id=tenant_id, agent_id=agent_id,
                               event=AUDIT_EVENT_STARTED)

            try:
                agent = await agent_service.get_agent(tenant_id, agent_id)
                request = RunRequest(task=task, model=model)
                # run_agent() handles the completed status update internally when run_id provided
                await run_agent(agent, request, tenant_id, run_id=run_id)
                logger.info("Worker: run_id=%s completed", run_id)

            except HTTPException as exc:
                logger.warning(
                    "Worker: run_id=%s failed HTTP %d: %s",
                    run_id, exc.status_code, exc.detail
                )
                await run.update({"$set": {
                    "status": RUN_STATUS_FAILED,
                    "completed_at": datetime.now(timezone.utc),
                    "error_message": str(exc.detail),
                }})
                await record_event(run_id=run_id, tenant_id=tenant_id, agent_id=agent_id,
                                   event=AUDIT_EVENT_FAILED,
                                   metadata={"error_message": str(exc.detail)})

            except Exception as exc:
                logger.exception("Worker: run_id=%s unexpected error: %s", run_id, exc)
                await run.update({"$set": {
                    "status": RUN_STATUS_FAILED,
                    "completed_at": datetime.now(timezone.utc),
                    "error_message": "Internal error during agent execution.",
                }})
                await record_event(run_id=run_id, tenant_id=tenant_id, agent_id=agent_id,
                                   event=AUDIT_EVENT_FAILED,
                                   metadata={"error_message": "Internal error during agent execution."})

    finally:
        tenant_ctx.reset(_token)


class WorkerSettings:
    """ARQ WorkerSettings — consumed by `arq app.worker.WorkerSettings`."""
    functions = [run_agent_task]
    redis_settings = ArqRedisSettings.from_dsn(settings.REDIS_URL)
    on_startup = _arq_startup
    on_shutdown = _arq_shutdown
    max_jobs = 10
    job_timeout = 300  # 5 minutes per run


logger.info("Worker: connecting to Redis at %s", settings.REDIS_URL_SAFE)
