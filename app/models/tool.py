"""
Tool domain model — powered by Beanie ODM.

Beanie automatically handles the `_id` to `id` conversion using `PydanticObjectId`.
Beanie handles database interactions directly on the object.
"""

from datetime import datetime, timezone
from pydantic import Field
from beanie import Document
from pymongo import IndexModel, ASCENDING

class Tool(Document):
    tenant_id: str
    name: str
    description: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name="tools" # Collection name in MongoDB
        indexes = [
            IndexModel([("tenant_id", ASCENDING)])
        ]