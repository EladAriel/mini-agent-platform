"""
Agent CRUD — Beanie ODM queries against the 'agents' collection.

Tool relationship
-----------------
The Agent model declares `tools: list[Link[Tool]]`. Beanie stores DBRefs
in MongoDB and can resolve them on demand. We use `fetch_links=True` on
reads so callers always receive fully-populated Tool objects, keeping the
resolution step implicit and consistent.
"""

from datetime import datetime, timezone

from beanie import PydanticObjectId
from fastapi import HTTPException, status

from app.core.logging import get_logger
from app.models.agent import Agent
from app.models.tool import Tool
from app.schemas.agent import AgentCreate, AgentUpdate
from app.services.service_helpers import parse_id, not_found

logger = get_logger(__name__)

async def _resolve_tools(
        tenant_id: str,
        tools_ids: list[str]
) -> list[Tool]:
    """
    Validate that every tool_id exists and belongs to this tenant,
    then return the full Tool documents in a single query.

    Example:
        #### INPUT
        tenant_id = "tenant_abc"
        tool_ids  = ["64b1...e1", "64b1...e2"]

        #### STEP 1 — parse strings to PydanticObjectId
        oids = [PydanticObjectId("64b1...e1"), PydanticObjectId("64b1...e2")]

        #### STEP 2 — Beanie runs:
        ####   db.tools.find({ "_id": { "$in": [...] }, "tenant_id": "tenant_abc" })
        tools = [Tool(id="64b1...e1", name="Web Search", ...), Tool(id="64b1...e2", name="Code Executor", ...)]

        #### HAPPY PATH — all IDs found
        #### OUTPUT
        [Tool(id="64b1...e1", ...), Tool(id="64b1...e2", ...)]

        #### UNHAPPY PATH A — a tool_id is not a valid ObjectId string
        tool_ids = ["not-valid"]
        #### → HTTPException(422, "One or more tool IDs are not valid ObjectId strings.")

        #### UNHAPPY PATH B — a tool_id doesn't exist or belongs to another tenant
        tool_ids = ["64b1...e1", "000000000000000000000000"]
        #### → HTTPException(422, "Tool IDs not found for this tenant: ['000000000000000000000000']")
    """
    if not tools_ids:
        return []

    try:
        oids = [PydanticObjectId(tool_id) for tool_id in tools_ids]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="One or more tool IDs are not valid ObjectId strings.",
        )
    
    tools = await Tool.find(
        {"_id": {"$in": oids}},
        Tool.tenant_id == tenant_id,
    ).to_list()

    if len(tools) != len(tools_ids):
        found = {str(tool.id) for tool in tools}
        missing = sorted(set(tools_ids) - found)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Tool IDs not found for this tenant: {missing}",
        )

    return tools

async def create_agent(
        tenant_id: str,
        data: AgentCreate
) -> Agent:
    """
    Validate tools, then insert a new agent document into the 'agents' collection.

    Example:
        #### INPUT
        tenant_id = "tenant_abc"
        data = AgentCreate(
            name="Research Bot",
            role="Research Assistant",
            description="Finds and summarises information from the web.",
            tool_ids=["64b1...e1", "64b1...e2"],
        )

        #### STEP 1 — validate tool IDs and fetch full Tool objects
        tools = [Tool(id="64b1...e1", name="Web Search", ...), Tool(id="64b1...e2", name="Code Executor", ...)]

        #### STEP 2 — build the Beanie document in memory (id is None, no DB yet)
        agent = Agent(tenant_id="tenant_abc", name="Research Bot", tools=[...], ...)

        #### STEP 3 — await agent.insert() writes to MongoDB and populates agent.id
        #### OUTPUT
        Agent(
            id          = "64c2a3b4e5f6a7b8c9d0e1f2",
            tenant_id   = "tenant_abc",
            name        = "Research Bot",
            role        = "Research Assistant",
            description = "Finds and summarises information from the web.",
            tools       = [Tool(id="64b1...e1", ...), Tool(id="64b1...e2", ...)],
            created_at  = datetime(2024, 1, 15, 10, 0, 0),
            updated_at  = datetime(2024, 1, 15, 10, 0, 0),
        )
    """
    logger.info("Creating agent: name=%s tenant=%s", data.name, tenant_id)
    tools = await _resolve_tools(tenant_id, data.tool_ids)
    agent = Agent(
        tenant_id=tenant_id,
        name=data.name,
        role=data.role,
        description=data.description,
        tools=tools
    )
    await agent.insert()
    logger.debug("Agent created successfully: id=%s", agent.id)
    return agent

async def get_agent(
        tenant_id: str,
        agent_id: str
) -> Agent:
    """
    Fetch a single agent by ID, scoped to the given tenant, with tools resolved.

    Example:
        #### INPUT
        tenant_id = "tenant_abc"
        agent_id  = "64c2a3b4e5f6a7b8c9d0e1f2"

        #### STEP 1 — _parse_id converts the raw string
        oid = PydanticObjectId("64c2a3b4e5f6a7b8c9d0e1f2")

        #### STEP 2 — Beanie runs (fetch_links=True resolves the tools[] DBRefs in the same call):
        ####   db.agents.find_one({ "_id": ObjectId("64c2a3..."), "tenant_id": "tenant_abc" })

        #### HAPPY PATH
        Agent(id="64c2a3...", name="Research Bot", tools=[Tool(...), Tool(...)], ...)

        #### UNHAPPY PATH A — agent belongs to a different tenant
        tenant_id = "tenant_xyz"
        #### → find_one returns None → HTTPException(404, "Agent not found.")

        #### UNHAPPY PATH B — agent does not exist at all
        agent_id = "000000000000000000000000"
        #### → find_one returns None → HTTPException(404, "Agent not found.")
    """
    logger.debug("Fetching agent: id=%s tenant=%s", agent_id, tenant_id)
    agent = await Agent.find_one(
        Agent.id == parse_id(agent_id, "Agent not found."),
        Agent.tenant_id == tenant_id,
        fetch_links=True,
    )

    if not agent:
        logger.warning("Agent not found: id=%s tenant=%s", agent_id, tenant_id)
        raise not_found("Agent not found.")

    logger.debug("Agent fetched successfully: id=%s", agent.id)
    return agent

async def list_agents(
        tenant_id: str,
        tool_name: str | None = None
) -> list[Agent]:
    """
    Return all agents for a tenant, with an optional tool-name filter.

    Example:
        #### ── Scenario A: no filter ─────────────────────────────────────────────
        #### INPUT
        tenant_id = "tenant_abc"
        tool_name = None

        #### Beanie runs: db.agents.find({ "tenant_id": "tenant_abc" })
        #### OUTPUT
        [
            Agent(id="64c2...f2", name="Research Bot",  tools=[Tool(name="Web Search"), ...]),
            Agent(id="64c2...f3", name="Code Agent",    tools=[Tool(name="Code Executor")]),
        ]

        #### ── Scenario B: filter by tool_name ───────────────────────────────────
        #### INPUT
        tool_name = "search"

        #### STEP 1 — fetch all agents with links resolved
        agents = [
            Agent(name="Research Bot", tools=[Tool(name="Web Search"), Tool(name="Code Executor")]),
            Agent(name="Code Agent",   tools=[Tool(name="Code Executor")]),
        ]

        #### STEP 2 — keep only agents that have at least one tool matching "search"
        #### "Research Bot"  → "Web Search".lower() contains "search" ✓  → kept
        #### "Code Agent"    → no tool name contains "search"           → dropped

        #### OUTPUT
        [Agent(name="Research Bot", tools=[Tool(name="Web Search"), Tool(name="Code Executor")])]

        #### ── Scenario C: no agents match the filter ────────────────────────────
        tool_name = "translator"
        #### → no tool names contain "translator" → returns []
    """
    logger.debug("Listing agents: tenant=%s tool_name=%s", tenant_id, tool_name)
    agents = await Agent.find(
        Agent.tenant_id == tenant_id,
        fetch_links=True,
    ).to_list()

    if tool_name is None:
        logger.debug("Listed %d agents for tenant=%s", len(agents), tenant_id)
        return agents

    filtered = [
        agent for agent in agents
        if any(tool_name.lower() in tool.name.lower() for tool in agent.tools)
    ]
    logger.debug("Filtered agents by tool_name='%s': %d results", tool_name, len(filtered))
    return filtered

async def update_agent(
        tenant_id: str,
        agent_id: str,
        data: AgentUpdate
) -> Agent:
    """
    Partially update an agent's fields. Only fields explicitly provided are changed.

    Example:
        #### INPUT
        tenant_id = "tenant_abc"
        agent_id  = "64c2a3b4e5f6a7b8c9d0e1f2"
        data      = AgentUpdate(name="Advanced Research Bot", role=None, tool_ids=[])

        #### STEP 1 — reuses get_agent() to fetch and validate (404 guard included)
        agent = Agent(id="64c2...", name="Research Bot", tools=[Tool(...), Tool(...)], ...)

        #### STEP 2 — build the updates dict; exclude_none=True drops untouched fields
        ####   name     → "Advanced Research Bot"  (explicitly provided)
        ####   role     → excluded                 (None means "don't touch it")
        ####   tool_ids → []                       (explicit [] means "remove all tools")

        #### STEP 3 — tool_ids=[] triggers _resolve_tools, which returns [] immediately
        tools = []

        #### STEP 4 — Beanie runs:
        ####   db.agents.update_one({ "_id": ObjectId("64c2a3...") }, { "$set": updates })

        #### STEP 5 — agent.sync() re-fetches so we return exactly what's stored
        #### OUTPUT
        Agent(
            id          = "64c2a3b4e5f6a7b8c9d0e1f2",
            name        = "Advanced Research Bot",  # ← updated
            role        = "Research Assistant",      # ← unchanged
            tools       = [],                        # ← cleared
            updated_at  = datetime(2024, 1, 15, 11, 0, 0),  # ← bumped
        )

        #### UNHAPPY PATH — agent not found
        #### get_agent() raises HTTPException(404) before any updates are built
    """
    logger.info("Updating agent: id=%s tenant=%s", agent_id, tenant_id)
    agent = await get_agent(tenant_id, agent_id)

    updates: dict = {
        "updated_at": datetime.now(timezone.utc)
    }

    if data.name is not None:
        updates["name"] = data.name
        logger.debug("Updating agent name to: %s", data.name)
    if data.role is not None:
        updates["role"] = data.role
        logger.debug("Updating agent role to: %s", data.role)
    if data.description is not None:
        updates["description"] = data.description
    if data.tool_ids is not None:
        tools = await _resolve_tools(tenant_id, data.tool_ids)
        updates["tools"] = [tool.to_ref() for tool in tools]
        logger.debug("Updating agent tools: %d tools", len(tools))

    await agent.update({"$set": updates})
    logger.info("Agent updated successfully: id=%s", agent_id)
    return await get_agent(tenant_id, agent_id)

async def delete_agent(
        tenant_id: str,
        agent_id: str
) -> None:
    """
    Permanently delete an agent. Returns None (HTTP 204 No Content).

    Example:
        #### INPUT
        tenant_id = "tenant_abc"
        agent_id  = "64c2a3b4e5f6a7b8c9d0e1f2"

        #### STEP 1 — reuses get_agent() to validate existence and tenant ownership
        agent = Agent(id="64c2a3b4e5f6a7b8c9d0e1f2", ...)

        #### STEP 2 — Beanie runs:
        ####   db.agents.delete_one({ "_id": ObjectId("64c2a3...") })

        #### OUTPUT — None

        #### UNHAPPY PATH — agent not found or belongs to another tenant
        #### get_agent() raises HTTPException(404) before delete is ever attempted
        #### The DB is never touched — no wasted round-trip
    """
    logger.info("Deleting agent: id=%s tenant=%s", agent_id, tenant_id)
    logger.info("Deleting agent: id=%s tenant=%s", agent_id, tenant_id)
    agent = await get_agent(tenant_id, agent_id)
    await agent.delete()
    logger.info("Agent deleted successfully: id=%s", agent_id)
    logger.info("Agent deleted successfully: id=%s", agent_id)