"""Global run history endpoints (across all agents)."""

from fastapi import APIRouter, Depends, Query

from app.core.logging import get_logger
from app.core.security import resolve_tenant
from app.schemas.run import PaginatedRuns, RunRead
from app.services.run_service import list_runs, get_run, _to_schema

logger = get_logger(__name__)

router = APIRouter(
    prefix="/runs",
    tags=["Runs"]
)

@router.get(
    "/{run_id}",
    response_model=RunRead,
    summary="Get run status",
    description=(
        "Retrieve the current state of a single run by its ID. "
        "Poll this endpoint until `status` is `completed` or `failed`. "
        "Returns 404 if the run does not exist or belongs to a different tenant."
    ),
)
async def get_run_status(
    run_id: str,
    tenant_id: str = Depends(resolve_tenant),
):
    logger.debug("API: Get run status request: run_id=%s", run_id)
    run = await get_run(tenant_id, run_id)
    return _to_schema(run)

@router.get(
    "",
    response_model=PaginatedRuns,
    summary="List all runs",
    description=(
        "Return a paginated history of all runs across every agent for the "
        "authenticated tenant, ordered by most recent first. "
        "Use `page` and `page_size` to navigate large result sets."
    ),
)
async def get_all_runs(
    page: int = Query(1, ge=1, description="Page number, starting from 1."),
    page_size: int = Query(20, ge=1, le=100, description="Number of runs per page (max 100)."),
    tenant_id: str = Depends(resolve_tenant),
):
    logger.debug("API: List all runs request: page=%d", page)
    return await list_runs(
        tenant_id,
        page=page,
        page_size=page_size
    )