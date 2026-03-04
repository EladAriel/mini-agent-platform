"""Agent management and execution endpoints."""

from fastapi import APIRouter, Depends, Query, status

from app.core.logging import get_logger
from app.core.security import resolve_tenant
from app.schemas.agent import AgentCreate, AgentRead, AgentUpdate
from app.schemas.run import PaginatedRuns, RunRequest, RunResponse
from app.schemas.tool import ToolRead
from app.services import agent_service
from app.services.run_service import list_runs
from app.services.runner.executor import run_agent

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
        tools=[
            ToolRead(
                id=str(tool.id),
                name=tool.name,
                description=tool.description,
                created_at=tool.created_at,
                updated_at=tool.updated_at
            ) for tool in agent.tools
        ],
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
    logger.info("API: Create agent request: tenant=%s name=%s", tenant_id, body.name)
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
    logger.debug("API: List agents request: tenant=%s tool_name=%s", tenant_id, tool_name)
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
    logger.debug("API: Get agent request: tenant=%s agent_id=%s", tenant_id, agent_id)
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
    logger.info("API: Update agent request: tenant=%s agent_id=%s", tenant_id, agent_id)
    result = _to_read(
        await agent_service.update_agent(tenant_id, agent_id, body)
    )
    logger.info("API: Agent updated: id=%s", result.id)
    return result

@router.delete(
    "/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an agent",
    description="Permanently delete an agent. Returns 404 if the agent does not exist or belongs to a different tenant.",
)
async def delete_agent(
    agent_id: str,
    tenant_id: str = Depends(resolve_tenant)
):
    logger.info("API: Delete agent request: tenant=%s agent_id=%s", tenant_id, agent_id)
    await agent_service.delete_agent(tenant_id, agent_id)
    logger.info("API: Agent deleted: id=%s", agent_id)

@router.post(
    "/{agent_id}/run",
    response_model=RunResponse,
    summary="Run an agent",
    description=(
        "Execute an agent against a given task using the specified model. "
        "The agent will use its assigned tools to complete the task and return "
        "a full run record including tool call traces and the final response."
    ),
)
async def run_agent_endpoint(
    agent_id: str,
    body: RunRequest,
    tenant_id: str = Depends(resolve_tenant),
):
    logger.info("API: Run agent request: tenant=%s agent_id=%s model=%s", tenant_id, agent_id, body.model)
    agent = await agent_service.get_agent(tenant_id, agent_id)
    return await run_agent(agent, body, tenant_id)

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
    logger.debug("API: Get agent runs request: tenant=%s agent_id=%s page=%d", tenant_id, agent_id, page)
    await agent_service.get_agent(tenant_id, agent_id)
    return await list_runs(
        tenant_id,
        agent_id=agent_id,
        page=page,
        page_size=page_size
    )