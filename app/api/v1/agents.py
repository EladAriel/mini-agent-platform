"""Agent management and execution endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from opentelemetry import propagate as otel_propagate

from app.core.logging import get_logger
from app.core.rate_limit import limiter
from app.core.security import resolve_tenant
from app.core.config import settings
from app.models.run import AgentRun, RUN_STATUS_PENDING
from app.schemas.agent import AgentCreate, AgentRead, AgentUpdate
from app.schemas.run import PaginatedRuns, RunRequest, RunSubmitted
from app.services import agent_service
from app.services.audit_service import record_event
from app.services.run_service import list_runs
from app.services.runner.guardrail import check_for_injection, PromptInjectionError
from app.services.runner.pii import anonymize_text
from app.api.v1.tools import _to_read as _tool_to_read
from app.models.audit import AUDIT_EVENT_CREATED

logger = get_logger(__name__)

router = APIRouter(
    prefix="/agents",
    tags=["Agents"]
)

def _to_read(agent) -> AgentRead:
    return AgentRead(
        id=str(agent.id),
        name=agent.name,
        role=agent.role,
        description=agent.description,
        tools=[_tool_to_read(tool) for tool in agent.tools],
        created_at=agent.created_at,
        updated_at=agent.updated_at,
    )

@router.post(
    "",
    response_model=AgentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create an agent",
    description=(
        "Register a new agent for the authenticated tenant. "
        "Optionally assign existing tools by passing their IDs in `tool_ids`. "
        "All tool IDs must belong to the same tenant, otherwise a 422 is returned."
    ),
)
async def create_agent(
    body: AgentCreate,
    tenant_id: str = Depends(resolve_tenant)
):
    logger.info("API: Create agent request: name=%s", body.name)
    result = _to_read(
        await agent_service.create_agent(tenant_id, body)
    )
    logger.info("API: Agent created: id=%s", result.id)
    return result

@router.get(
    "",
    response_model=list[AgentRead],
    summary="List agents",
    description=(
        "Return all agents belonging to the authenticated tenant. "
        "Optionally filter by `tool_name` to return only agents that have at least "
        "one tool whose name contains that string (case-insensitive)."
    ),    
)
async def list_agents(
    tool_name: str | None = Query(None, description="Filter agents by tool name (partial match)."),
    tenant_id: str = Depends(resolve_tenant),
):
    logger.debug("API: List agents request: tool_name=%s", tool_name)
    return [
        _to_read(agent) for agent in await agent_service.list_agents(tenant_id, tool_name)
    ]

@router.get(
    "/{agent_id}",
    response_model=AgentRead,
    summary="Get an agent",
    description="Retrieve a single agent by its ID. Returns 404 if the agent does not exist or belongs to a different tenant.",
)
async def get_agent(
    agent_id: str,
    tenant_id: str = Depends(resolve_tenant)
):
    logger.debug("API: Get agent request: agent_id=%s", agent_id)
    return _to_read(
        await agent_service.get_agent(tenant_id, agent_id)
    )

@router.patch(
    "/{agent_id}",
    response_model=AgentRead,
    summary="Update an agent",
    description=(
        "Partially update an agent's fields. Only the fields that are provided will be changed. "
        "Pass `tool_ids: []` to remove all tools, or omit `tool_ids` entirely to leave them unchanged."
    ),
)
async def update_agent(
    agent_id: str,
    body: AgentUpdate,
    tenant_id: str = Depends(resolve_tenant)
):
    logger.info("API: Update agent request: agent_id=%s", agent_id)
    result = _to_read(
        await agent_service.update_agent(tenant_id, agent_id, body)
    )
    logger.info("API: Agent updated: id=%s", result.id)
    return result

@router.delete(
    "/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an agent",
    description="Soft-delete an agent (sets deleted_at). The agent is excluded from all future queries. Returns 404 if the agent does not exist or belongs to a different tenant.",
)
async def delete_agent(
    agent_id: str,
    tenant_id: str = Depends(resolve_tenant)
):
    logger.info("API: Delete agent request: agent_id=%s", agent_id)
    await agent_service.delete_agent(tenant_id, agent_id)
    logger.info("API: Agent deleted: id=%s", agent_id)

@router.post(
    "/{agent_id}/run",
    response_model=RunSubmitted,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit an agent run",
    description=(
        "Enqueue an agent execution against a given task. "
        "Returns HTTP 202 immediately with a `run_id`. "
        "Poll `GET /runs/{run_id}` until `status` is `completed` or `failed`."
    ),
)
@limiter.limit(settings.RATE_LIMIT_RUN_ENDPOINT)
async def run_agent_endpoint(
    agent_id: str,
    body: RunRequest,
    request: Request,
    response: Response,
    tenant_id: str = Depends(resolve_tenant),
):
    logger.info("API: Run agent request: agent_id=%s model=%s", agent_id, body.model)

    # 404 guard — verify the agent exists before creating any document
    agent = await agent_service.get_agent(tenant_id, agent_id)

    # Injection guard at submit time — fast reject before a pending doc is created
    # detail is intentionally generic: returning str(exc) would leak the matched
    # pattern and text, enabling attackers to iterate payloads to bypass detection.
    try:
        check_for_injection(body.task)
    except PromptInjectionError as exc:
        logger.warning(
            "Injection attempt blocked: agent_id=%s category=%s",
            agent_id, exc.category,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request blocked: input policy violation.",
        ) from exc

    # Anonymize the task before any persistence or logging — PII is replaced
    # with labeled placeholders (e.g. <PERSON>, <EMAIL_ADDRESS>) at the API
    # layer so neither the DB document nor log lines ever contain raw PII.
    # Injection check runs first on the raw string (safety order invariant).
    anon_task = anonymize_text(body.task)

    # Pre-create the pending run document so clients can poll immediately
    run = AgentRun(
        tenant_id=tenant_id,
        agent_id=str(agent.id),
        model=body.model,
        task=anon_task,
        status=RUN_STATUS_PENDING,
    )
    await run.insert()

    await record_event(
        run_id=str(run.id),
        tenant_id=tenant_id,
        agent_id=str(agent.id),
        event=AUDIT_EVENT_CREATED,
    )

    # Enqueue for async execution
    trace_carrier: dict[str, str] = {}
    otel_propagate.inject(trace_carrier)   # serializes active span as W3C traceparent

    await request.app.state.arq_pool.enqueue_job(
        "run_agent_task",
        run_id=str(run.id),
        agent_id=str(agent.id),
        tenant_id=tenant_id,
        task=anon_task,
        model=body.model,
        trace_carrier=trace_carrier,
    )
    logger.info("API: Run enqueued: run_id=%s agent_id=%s", run.id, agent_id)

    return RunSubmitted(
        run_id=str(run.id),
        status=RUN_STATUS_PENDING,
        agent_id=str(agent.id),
        model=body.model,
        created_at=run.created_at,
    )

@router.get(
    "/{agent_id}/runs",
    response_model=PaginatedRuns,
    summary="List agent runs",
    description=(
        "Return a paginated history of all runs for a specific agent. "
        "Use `page` and `page_size` to navigate large result sets. "
        "Returns 404 if the agent does not exist or belongs to a different tenant."
    ),    
)
async def get_agent_runs(
    agent_id: str,
    page: int = Query(1, ge=1, description="Page number, starting from 1."),
    page_size: int = Query(20, ge=1, le=100, description="Number of runs per page (max 100)."),
    tenant_id: str = Depends(resolve_tenant),
):
    logger.debug("API: Get agent runs request: agent_id=%s page=%d", agent_id, page)
    await agent_service.get_agent(tenant_id, agent_id)
    return await list_runs(
        tenant_id,
        agent_id=agent_id,
        page=page,
        page_size=page_size
    )