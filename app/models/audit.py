# IMMUTABLE — insert() only, never update() or delete()
from datetime import datetime, timezone
from typing import Any

from beanie import Document
from pydantic import Field
from pymongo import ASCENDING, DESCENDING, IndexModel

AUDIT_EVENT_CREATED   = "created"
AUDIT_EVENT_STARTED   = "started"
AUDIT_EVENT_COMPLETED = "completed"
AUDIT_EVENT_FAILED    = "failed"


class AuditEvent(Document):
    run_id:      str
    tenant_id:   str
    agent_id:    str
    event:       str
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata:    dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "audit_events"
        indexes = [
            IndexModel([("run_id",      ASCENDING)]),
            IndexModel([("tenant_id",   ASCENDING)]),
            IndexModel([("occurred_at", DESCENDING)]),
            IndexModel([("tenant_id",   ASCENDING), ("run_id", ASCENDING)]),
        ]
