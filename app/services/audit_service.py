"""Append-only audit event writer.

All writes are fire-and-forget: any DB failure is caught and logged so that
audit issues never interrupt the main execution path.
"""
import json
from typing import Any

from app.core.logging import get_logger
from app.models.audit import AuditEvent

logger = get_logger(__name__)

MAX_METADATA_BYTES = 10_000


def _truncate_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """Return metadata truncated to MAX_METADATA_BYTES (JSON-serialized).

    If the payload exceeds the limit, replace it with a single sentinel key
    and log a warning.  The original dict is never mutated.
    """
    try:
        serialized = json.dumps(metadata)
    except (TypeError, ValueError):
        # Non-serializable metadata — replace entirely to avoid storing garbage.
        logger.warning("Audit metadata is not JSON-serializable; dropping payload.")
        return {"_truncated": True}

    byte_size = len(serialized.encode())
    if byte_size > MAX_METADATA_BYTES:
        logger.warning(
            "Audit metadata exceeds %d bytes; truncating. original_size=%d",
            MAX_METADATA_BYTES,
            byte_size,
        )
        return {"_truncated": True}

    return metadata


async def record_event(
    *,
    run_id:    str,
    tenant_id: str,
    agent_id:  str,
    event:     str,
    metadata:  dict[str, Any] | None = None,
) -> None:
    """Insert one AuditEvent document.  Never raises."""
    safe_metadata = _truncate_metadata(metadata or {})
    try:
        await AuditEvent(
            run_id=run_id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            event=event,
            metadata=safe_metadata,
        ).insert()
        logger.debug("Audit event recorded: run_id=%s event=%s", run_id, event)
    except Exception as exc:
        logger.error(
            "Failed to write audit event: run_id=%s event=%s error=%s",
            run_id, event, exc,
        )
