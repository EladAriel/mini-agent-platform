"""API-key authentication and tenant resolution."""

from fastapi import Header, HTTPException, status
from app.core.config import settings

def resolve_tenant(
        x_api_key: str | None = Header(None, alias="X-API-key")
) -> str:
    """
    FastAPI dependency: Acts as a security gatekeeper for multi-tenancy.
    
    Why this logic:
    - Extraction: Automatically pulls the 'X-API-key' from the request headers.
    - Validation: Checks the key against the trusted '.env' map. If invalid, 
      it halts the request with a 401 Unauthorized to protect system resources.
    - Isolation: Returns the 'tenant_id' so that every subsequent database 
      query is strictly scoped to that specific user's data.
    """
    tenant_id = settings.TENANT_API_KEYS.get(x_api_key)

    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )
    
    return tenant_id