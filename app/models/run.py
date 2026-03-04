"""
AgentRun domain model — powered by Beanie ODM.

ToolCallRecord remains a plain Pydantic BaseModel. Beanie natively 
understands how to embed it directly inside the AgentRun document.
"""

from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field
from beanie import Document
from pymongo import IndexModel, ASCENDING, DESCENDING

class ToolCallRecord(BaseModel):
    """A single tool invocation within an agent run."""
    step: int
    tool_name: str
    tool_input: str
    tool_output: str

class AgentRun(Document):
    tenant_id: str
    agent_id: str
    model: str
    task: str
    messages: list[dict[str, Any]] = Field(default_factory=list)
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)
    final_response: str | None = None
    steps: int = 0
    status: str = "success" # "success" | "error"
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
        ]