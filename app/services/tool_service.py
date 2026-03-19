"""
Tool CRUD — Beanie ODM queries against the 'tools' collection.
"""

from datetime import datetime, timezone

from beanie import PydanticObjectId
from fastapi import HTTPException, status

from app.core.logging import get_logger
from app.models.agent import Agent
from app.models.tool import Tool
from app.schemas.tool import ToolCreate, ToolUpdate
from app.services.service_helpers import parse_id, not_found

logger = get_logger(__name__)

async def create_tool(
        tenant_id: str,
        data: ToolCreate
) -> Tool:
    """
    Insert a new tool document into the 'tools' collection.

    Example:
        #### INPUT
        tenant_id = "tenant_abc"
        data = ToolCreate(name="Web Search", description="Searches the web.")

        #### STEP 1 — build the Beanie document in memory (no DB yet, id is None)
        tool = Tool(tenant_id="tenant_abc", name="Web Search", description="Searches the web.", ...)

        #### STEP 2 — await tool.insert() writes to MongoDB and populates tool.id
        #### OUTPUT
        Tool(id="64b1f2c3d4e5f6a7b8c9d0e1", tenant_id="tenant_abc", name="Web Search", ...)
    """    
    logger.info("Creating tool: name=%s", data.name)

    # Check for duplicate tool name within the tenant (exclude soft-deleted)
    existing = await Tool.find_one(
        Tool.tenant_id == tenant_id,
        Tool.name == data.name,
        Tool.deleted_at == None,
    )
    if existing:
        logger.warning("Tool name already exists: name=%s", data.name)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tool with name '{data.name}' already exists for this tenant."
        )

    tool = Tool(tenant_id=tenant_id, **data.model_dump())
    await tool.insert()
    logger.debug("Tool created successfully: id=%s", tool.id)
    return tool

async def get_tool(
        tenant_id: str,
        tool_id: str
) -> Tool:
    """
    Fetch a single tool by ID, scoped to the given tenant.

    Example:
        #### INPUT
        tenant_id = "tenant_abc"
        tool_id   = "64b1f2c3d4e5f6a7b8c9d0e1"

        #### STEP 1 — _parse_id converts the raw string
        oid = PydanticObjectId("64b1f2c3d4e5f6a7b8c9d0e1")

        #### STEP 2 — Beanie runs:
        ####   db.tools.find_one({ "_id": ObjectId("64b1f2..."), "tenant_id": "tenant_abc" })

        #### HAPPY PATH
        Tool(id="64b1f2c3d4e5f6a7b8c9d0e1", tenant_id="tenant_abc", name="Web Search", ...)

        #### UNHAPPY PATH A — tool belongs to a different tenant
        tenant_id = "tenant_xyz"
        #### → find_one returns None → HTTPException(404, "Tool not found.")

        #### UNHAPPY PATH B — tool does not exist at all
        tool_id = "000000000000000000000000"
        #### → find_one returns None → HTTPException(404, "Tool not found.")
    """    
    logger.debug("Fetching tool: id=%s", tool_id)
    tool = await Tool.find_one(
        Tool.id == parse_id(tool_id, "Tool not found."),
        Tool.tenant_id == tenant_id,
        Tool.deleted_at == None,
    )

    if not tool:
        logger.warning("Tool not found: id=%s", tool_id)
        raise not_found("Tool not found.")

    logger.debug("Tool fetched successfully: id=%s", tool.id)
    return tool

async def list_tools(
        tenant_id: str,
        agent_name: str | None = None
) -> list[Tool]:
    """
    Return all tools for a tenant, with an optional agent-name filter.

    Example:
        #### ── Scenario A: no filter ─────────────────────────────────────────────
        #### INPUT
        tenant_id  = "tenant_abc"
        agent_name = None

        #### Beanie runs: db.tools.find({ "tenant_id": "tenant_abc" })
        #### OUTPUT
        [
            Tool(id="64b1f2c3d4e5f6a7b8c9d0e1", name="Web Search",    ...),
            Tool(id="64b1f2c3d4e5f6a7b8c9d0e2", name="Code Executor",  ...),
        ]

        #### ── Scenario B: filter by agent_name ──────────────────────────────────
        #### INPUT
        agent_name = "research"

        #### STEP 1 — find agents whose name matches (case-insensitive regex)
        ####   db.agents.find({ "tenant_id": "tenant_abc", "name": { "$regex": "research", "$options": "i" } })
        agents = [
            Agent(name="Research Bot",        tools=[Ref("64b1...e1"), Ref("64b1...e2")]),
            Agent(name="Deep Research Agent", tools=[Ref("64b1...e1"), Ref("64b1...e3")]),
        ]

        #### STEP 2 — extract ObjectIds from all link refs (duplicates are fine, $in handles them)
        tool_ids = ["64b1...e1", "64b1...e2", "64b1...e3"]

        #### STEP 3 — Beanie runs:
        ####   db.tools.find({ "_id": { "$in": [...] }, "tenant_id": "tenant_abc" })
        #### OUTPUT
        [
            Tool(id="64b1...e1", name="Web Search",    ...),
            Tool(id="64b1...e2", name="Code Executor",  ...),
            Tool(id="64b1...e3", name="File Reader",    ...),
        ]

        #### ── Scenario C: agents match but have no tools ────────────────────────
        agents   = [Agent(name="Research Bot", tools=[])]
        tool_ids = []
        #### → short-circuits immediately, returns [] without a second DB query
    """    
    logger.debug("Listing tools: agent_name=%s", agent_name)
    if not agent_name:
        tools = await Tool.find(
            Tool.tenant_id == tenant_id,
            Tool.deleted_at == None,
        ).to_list()
        logger.debug("Listed %d tools", len(tools))
        return tools

    agents = await Agent.find(
        Agent.tenant_id == tenant_id,
        {"name": {"$regex": agent_name, "$options": "i"}}
    ).to_list()

    tool_ids: list[PydanticObjectId] = [
        link.ref.id for agent in agents for link in (agent.tools or [])
    ]

    if not tool_ids:
        logger.debug("No tools found for agent_name='%s'", agent_name)
        return []

    tools = await Tool.find(
        {"_id": {"$in": tool_ids}},
        Tool.tenant_id == tenant_id,
        Tool.deleted_at == None,
    ).to_list()
    logger.debug("Filtered tools by agent_name='%s': %d results", agent_name, len(tools))
    return tools

async def update_tool(
        tenant_id: str,
        tool_id: str,
        data: ToolUpdate
) -> Tool:
    """
    Partially update a tool's fields. Only fields explicitly provided are changed.

    Example:
        #### INPUT
        tenant_id = "tenant_abc"
        tool_id   = "64b1f2c3d4e5f6a7b8c9d0e1"
        data      = ToolUpdate(name="Advanced Web Search", description=None)

        #### STEP 1 — reuses get_tool() to fetch and validate (404 guard included)
        tool = Tool(id="64b1...e1", name="Web Search", description="Searches the web.", ...)

        #### STEP 2 — exclude_none=True drops fields the caller didn't send
        updates = {
            "name": "Advanced Web Search",
            # description excluded — None means "don't touch it"
            "updated_at": datetime(2024, 1, 15, 11, 0, 0),
        }

        #### STEP 3 — Beanie runs:
        ####   db.tools.update_one({ "_id": ObjectId("64b1f2...") }, { "$set": updates })

        #### STEP 4 — tool.sync() re-fetches so we return exactly what's stored
        #### OUTPUT
        Tool(
            id          = "64b1f2c3d4e5f6a7b8c9d0e1",
            name        = "Advanced Web Search",  # ← updated
            description = "Searches the web.",    # ← unchanged
            updated_at  = datetime(2024, 1, 15, 11, 0, 0),  # ← bumped
        )

        #### UNHAPPY PATH — tool not found
        #### get_tool() raises HTTPException(404) before updates are even built
    """    
    logger.info("Updating tool: id=%s", tool_id)
    tool = await get_tool(tenant_id, tool_id)
    updates = data.model_dump(exclude_none=True)
    updates["updated_at"] = datetime.now(timezone.utc)

    # Check for duplicate name if renaming
    if "name" in updates and updates["name"] != tool.name:
        existing = await Tool.find_one(
            Tool.tenant_id == tenant_id,
            Tool.name == updates["name"],
            Tool.deleted_at == None,
        )
        if existing:
            logger.warning(
                "Cannot update tool: name '%s' already exists",
                updates["name"]
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Tool with name '{updates['name']}' already exists for this tenant."
            )

    if updates:
        logger.debug("Applying updates to tool %s: %s", tool_id, list(updates.keys()))

    await tool.update({"$set": updates})
    logger.info("Tool updated successfully: id=%s", tool_id)

    # return the document as stored after the update
    return await get_tool(tenant_id, tool_id)

async def delete_tool(
        tenant_id: str,
        tool_id: str
) -> None:
    """
    Permanently delete a tool. Returns None (HTTP 204 No Content).

    Example:
        #### INPUT
        tenant_id = "tenant_abc"
        tool_id   = "64b1f2c3d4e5f6a7b8c9d0e1"

        #### STEP 1 — reuses get_tool() to validate existence and tenant ownership
        tool = Tool(id="64b1f2c3d4e5f6a7b8c9d0e1", ...)

        #### STEP 2 — Beanie runs:
        ####   db.tools.delete_one({ "_id": ObjectId("64b1f2...") })

        #### OUTPUT — None

        #### UNHAPPY PATH — tool not found or belongs to another tenant
        #### get_tool() raises HTTPException(404) before delete is ever attempted
        #### The DB is never touched — no wasted round-trip
    """    
    logger.info("Deleting tool: id=%s", tool_id)
    tool = await get_tool(tenant_id, tool_id)
    await tool.update({"$set": {"deleted_at": datetime.now(timezone.utc)}})
    logger.info("Tool soft-deleted: id=%s", tool_id)