"""Tool management and execution endpoints."""

from fastapi import APIRouter, Depends, Query, status

from app.core.logging import get_logger
from app.core.security import resolve_tenant
from app.schemas.tool import ToolCreate, ToolRead, ToolUpdate
from app.services import tool_service

logger = get_logger(__name__)

router = APIRouter(
    prefix="/tools",
    tags=["Tools"]
)

def _to_read(tool) -> ToolRead:
    return ToolRead(
        id=str(tool.id),
        name=tool.name,
        description=tool.description,
        created_at=tool.created_at,
        updated_at=tool.updated_at,
    )

@router.post(
        "",
        status_code=status.HTTP_201_CREATED,
        response_model=ToolRead,
        summary="Create a tool",
        description="Register a new tool for the authenticated tenant. The tool can later be assigned to one or more agents.",
)
async def create_tool(
    body: ToolCreate,
    tenant_id: str = Depends(resolve_tenant)
):
    logger.info("API: Create tool request: name=%s", body.name)
    result = _to_read(
        await tool_service.create_tool(tenant_id, body)
    )
    logger.info("API: Tool created: id=%s", result.id)
    return result

@router.get(
        "",
        response_model=list[ToolRead],
        summary="List tools",
        description=(
            "Return all tools belonging to the authenticated tenant. "
            "Optionally filter by `agent_name` to return only the tools "
            "assigned to agents whose name contains that string (case-insensitive)."
        ),        
)
async def list_tools(
    agent_name: str | None = Query(None),
    tenant_id: str = Depends(resolve_tenant)
):
    logger.debug("API: List tools request: agent_name=%s", agent_name)
    return [
        _to_read(tool) for tool in await tool_service.list_tools(tenant_id, agent_name)
    ]

@router.get(
    "/{tool_id}",
    response_model=ToolRead,
    summary="Get a tool",
    description="Retrieve a single tool by its ID. Returns 404 if the tool does not exist or belongs to a different tenant.",
)
async def get_tool(
    tool_id: str,
    tenant_id: str = Depends(resolve_tenant)
):
    logger.debug("API: Get tool request: tool_id=%s", tool_id)
    return _to_read(
        await tool_service.get_tool(tenant_id, tool_id)
    )

@router.patch(
    "/{tool_id}",
    response_model=ToolRead,
    summary="Update a tool",
    description="Partially update a tool's name or description. Only the fields that are provided will be changed.",
)
async def update_tool(
    tool_id: str,
    body: ToolUpdate,
    tenant_id: str = Depends(resolve_tenant)
):
    logger.info("API: Update tool request: tool_id=%s", tool_id)
    result = _to_read(
        await tool_service.update_tool(tenant_id, tool_id, body)
    )
    logger.info("API: Tool updated: id=%s", result.id)
    return result

@router.delete(
    "/{tool_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a tool",
    description="Soft-delete a tool (sets deleted_at). The tool is excluded from all future queries. Returns 404 if the tool does not exist or belongs to a different tenant.",
)
async def delete_tool(
    tool_id: str,
    tenant_id: str = Depends(resolve_tenant)
):
    logger.info("API: Delete tool request: tool_id=%s", tool_id)
    await tool_service.delete_tool(tenant_id, tool_id)
    logger.info("API: Tool deleted: id=%s", tool_id)