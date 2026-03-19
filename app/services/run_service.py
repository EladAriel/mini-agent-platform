"""
Run history retrieval — Beanie ODM queries against the 'agent_runs' collection.
"""

import math

from fastapi import HTTPException

from app.core.logging import get_logger
from app.models.run import AgentRun
from app.schemas.run import PaginatedRuns, RunRead

logger = get_logger(__name__)

def _to_schema(run: AgentRun) -> RunRead:
    """
    Map a Beanie AgentRun document to the RunRead response schema.

    Example:
        #### INPUT
        run = AgentRun(
            id             = "64d3e4f5a6b7c8d9e0f1a2b3",
            agent_id       = "64c2a3b4e5f6a7b8c9d0e1f2",
            model          = "gpt-4o",
            task           = "Summarise the latest AI news.",
            tool_calls     = [ToolCallRecord(step=1, tool_name="Web Search",
                               tool_input="latest AI news", tool_output="...")],
            final_response = "Here is a summary...",
            steps          = 1,
            status         = "completed",
            created_at     = datetime(2024, 1, 15, 10, 0, 0),
        )

        #### OUTPUT
        RunRead(
            id             = "64d3e4f5a6b7c8d9e0f1a2b3",
            agent_id       = "64c2a3b4e5f6a7b8c9d0e1f2",
            model          = "gpt-4o",
            task           = "Summarise the latest AI news.",
            tool_calls     = [ToolCallRecord(step=1, tool_name="Web Search", ...)],
            final_response = "Here is a summary...",
            steps          = 1,
            status         = "completed",
            created_at     = datetime(2024, 1, 15, 10, 0, 0),
        )
    """
    return RunRead(
        id=str(run.id),
        agent_id=run.agent_id,
        model=run.model,
        task=run.task,
        tool_calls=run.tool_calls,
        final_response=run.final_response,
        steps=run.steps,
        status=run.status,
        error_message=run.error_message,
        started_at=run.started_at,
        completed_at=run.completed_at,
        created_at=run.created_at
    )

async def get_run(tenant_id: str, run_id: str) -> AgentRun:
    """
    Fetch a single AgentRun by ID scoped to the tenant.

    Raises HTTP 404 if the run_id is malformed, does not exist,
    or belongs to a different tenant.
    """
    from beanie import PydanticObjectId
    try:
        oid = PydanticObjectId(run_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Run not found.")
    run = await AgentRun.find_one(AgentRun.id == oid, AgentRun.tenant_id == tenant_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found.")
    return run

async def list_runs(
        tenant_id: str,
        agent_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
) -> PaginatedRuns:
    """
    Return a paginated, most-recent-first list of runs for a tenant.
    Optionally scoped to a single agent via `agent_id`.

    Example:
        #### ── Scenario A: all runs for a tenant ────────────────────────────────
        #### INPUT
        tenant_id = "tenant_abc"
        agent_id  = None
        page      = 1
        page_size = 20

        #### STEP 1 — build the query filter
        query = { "tenant_id": "tenant_abc" }

        #### STEP 2 — Beanie counts matching documents
        ####   db.agent_runs.count_documents({ "tenant_id": "tenant_abc" })
        total = 45

        #### STEP 3 — Beanie fetches the page, sorted by created_at descending
        ####   db.agent_runs.find(query).sort("created_at", -1).skip(0).limit(20)
        runs = [AgentRun(...), AgentRun(...), ...]  # 20 documents

        #### STEP 4 — compute pagination metadata
        pages = math.ceil(45 / 20)  # → 3

        #### OUTPUT
        PaginatedRuns(items=[RunRead(...), ...], total=45, page=1, page_size=20, pages=3)


        #### ── Scenario B: runs scoped to a specific agent ───────────────────────
        #### INPUT
        agent_id  = "64c2a3b4e5f6a7b8c9d0e1f2"
        page      = 2
        page_size = 20

        #### STEP 1 — query includes agent_id
        query = { "tenant_id": "tenant_abc", "agent_id": "64c2a3b4e5f6a7b8c9d0e1f2" }

        #### STEP 2 — count scoped to this agent
        total = 7

        #### STEP 3 — fetch page 2: skip=(2-1)*20=20, but only 7 docs exist
        runs = []  # page 2 is beyond the result set

        #### OUTPUT
        PaginatedRuns(items=[], total=7, page=2, page_size=20, pages=1)


        #### ── Scenario C: no runs exist yet ─────────────────────────────────────
        total = 0
        #### pages = max(1, ceil(0/20)) → 1  (never returns pages=0)
        #### OUTPUT
        PaginatedRuns(items=[], total=0, page=1, page_size=20, pages=1)
    """
    logger.debug("Listing runs: agent_id=%s page=%d page_size=%d", agent_id, page, page_size)
    query: dict = {"tenant_id": tenant_id}

    if agent_id:
        query["agent_id"] = agent_id

    match_stage = {"$match": query}
    pipeline = [
        {
            "$facet": {
                "total": [match_stage, {"$count": "n"}],
                "items": [
                    match_stage,
                    {"$sort": {"created_at": -1}},
                    {"$skip": (page - 1) * page_size},
                    {"$limit": page_size},
                ],
            }
        }
    ]

    results = await AgentRun.aggregate(pipeline).to_list()
    facet = results[0]

    total_list = facet.get("total", [])
    total = total_list[0]["n"] if total_list else 0

    items = [
        _to_schema(AgentRun.model_validate(raw))
        for raw in facet.get("items", [])
    ]
    logger.debug("Total runs found: %d", total)

    return PaginatedRuns(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=max(1, math.ceil(total / page_size)),
    )