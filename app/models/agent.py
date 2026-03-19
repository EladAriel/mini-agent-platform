"""
Agent domain model — powered by Beanie ODM.

Tool relationship
-----------------
By using Beanie's `Link`, MongoDB only stores the references (foreign keys) 
to the Tools. The application layer can fetch the full objects dynamically, 
keeping the DB document simple while removing the need for manual ID resolution.

Lazy Loading
------------
When user query the agent from the db (e.g. agent = await Agent.find_one(...)),
Beanie performs lazy loading by default. This means agent.tools will initially just be a list
of references, saving memory and db lookups until user actually need the full tool data.
"""

from datetime import datetime, timezone
from typing import Optional
from pydantic import Field
from beanie import Document, Link
from pymongo import IndexModel, ASCENDING

from app.models.tool import Tool

class Agent(Document):
    tenant_id: str
    name: str
    role: str
    description: str
    tools: list[Link[Tool]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = None

    class Settings:
        name = "agents" # Collection name in MongoDB
        indexes = [
            IndexModel([("tenant_id", ASCENDING)])
        ]