"""
Run history retrieval — Beanie ODM queries against the 'agent_runs' collection.
"""

import math

from app.core.logging import get_logger
from app.models.run import AgentRun
from app.schemas.run import PaginatedRuns, RunRead, ToolCallRecord

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
            status         = "success",
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
            status         = "success",
            created_at     = datetime(2024, 1, 15, 10, 0, 0),
        )
    """
    return RunRead(
        id=str(run.id),
        agent_id=run.agent_id,
        model=run.model,
        task=run.task,
        tool_calls=[
            ToolCallRecord(
                step=tool_call.step,
                tool_name=tool_call.tool_name,
                tool_input=tool_call.tool_input,
                tool_output=tool_call.tool_output
            ) for tool_call in run.tool_calls
        ],
        final_response=run.final_response,
        steps=run.steps,
        status=run.status,
        created_at=run.created_at
    )

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
    logger.debug("Listing runs: tenant=%s agent_id=%s page=%d page_size=%d", tenant_id, agent_id, page, page_size)
    query: dict = {"tenant_id": tenant_id}

    if agent_id:
        query["agent_id"] = agent_id

    total = await AgentRun.find(query).count()
    logger.debug("Total runs found: %d", total)

    runs = (
        await AgentRun.find(query)
        .sort(-AgentRun.created_at)
        .skip((page - 1) * page_size)
        .limit(page_size)
        .to_list()
    )

    return PaginatedRuns(
        items=[_to_schema(run) for run in runs],
        total=total,
        page=page,
        page_size=page_size,
        pages=max(1, math.ceil(total / page_size)),
    )