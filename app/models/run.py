"""
AgentRun domain model — powered by Beanie ODM.

ToolCallRecord is imported from schemas so there is a single definition shared
by both the API response layer and the DB model.
"""

from datetime import datetime, timezone
from typing import Any
from pydantic import Field
from beanie import Document
from pymongo import IndexModel, ASCENDING, DESCENDING

from app.schemas.run import ToolCallRecord  # noqa: F401 — re-exported for Beanie

# Run lifecycle status constants — single source of truth for every state transition
RUN_STATUS_PENDING   = "pending"
RUN_STATUS_RUNNING   = "running"
RUN_STATUS_COMPLETED = "completed"
RUN_STATUS_FAILED    = "failed"


class AgentRun(Document):
    tenant_id: str
    agent_id: str
    model: str
    task: str
    messages: list[dict[str, Any]] = Field(default_factory=list)
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)
    final_response: str | None = None
    steps: int = 0
    status: str = RUN_STATUS_PENDING
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "agent_runs" # Collection name in MongoDB
        indexes = [
            IndexModel([("tenant_id", ASCENDING)]),
            IndexModel([
                ("tenant_id", ASCENDING),
                ("agent_id", ASCENDING)
            ]),
            IndexModel([("created_at", DESCENDING)]),
            IndexModel([("status", ASCENDING)]),
        ]