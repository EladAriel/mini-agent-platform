"""Global run history endpoints (across all agents)."""

from fastapi import APIRouter, Depends, Query

from app.core.logging import get_logger
from app.core.security import resolve_tenant
from app.schemas.run import PaginatedRuns
from app.services.run_service import list_runs

logger = get_logger(__name__)

router = APIRouter(
    prefix="/runs",
    tags=["Runs"]
)

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
    logger.debug("API: List all runs request: tenant=%s page=%d", tenant_id, page)
    return await list_runs(
        tenant_id,
        page=page,
        page_size=page_size
    )