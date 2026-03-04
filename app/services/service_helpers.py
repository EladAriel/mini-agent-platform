"""
Shared helpers for service-layer functions.
"""

from beanie import PydanticObjectId
from fastapi import HTTPException, status


def parse_id(resource_id: str, detail: str = "Resource not found.") -> PydanticObjectId:
    """
    Convert a string to PydanticObjectId, raising 404 on malformed input.

    Args:
        resource_id: The raw string ID from the request path.
        detail:      The 404 message to return — should name the resource
                     (e.g. "Agent not found.", "Tool not found.").

    Example:
        parse_id("64b1f2c3d4e5f6a7b8c9d0e1", "Tool not found.")
        # → PydanticObjectId("64b1f2c3d4e5f6a7b8c9d0e1")

        parse_id("not-a-real-id", "Tool not found.")
        # → HTTPException(404, "Tool not found.")
    """
    try:
        return PydanticObjectId(resource_id)
    except Exception:
        raise not_found(detail)


def not_found(detail: str = "Resource not found.") -> HTTPException:
    """
    Return a 404 HTTPException with a caller-supplied message.

    Returning rather than raising keeps call sites readable:
        raise not_found("Agent not found.")

    Example:
        raise not_found("Agent not found.")
        # → HTTPException(404, "Agent not found.")
    """
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)