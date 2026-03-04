from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class ToolCreate(BaseModel):
    """
    Schema for creating a new Tool.
    
    Why these constraints:
    - min_length=1: Prevents 'invisible' tools with empty names that would break 
      the UI and create useless database entries.
    - max_length=200: A security guardrail to prevent 'resource exhaustion' attacks. 
      Without this, massive strings could bloat MongoDB storage, slow down the 
      network, and crash frontend rendering.
    """
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)

class ToolRead(BaseModel):
    """
    Schema for returning Tool data to the client.
    
    Why model_config:
    - from_attributes=True: Essential for Beanie integration. It allows Pydantic 
      to map data directly from the database object's attributes (like tool.name) 
      rather than requiring a standard Python dictionary.
    """    
    id: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ToolUpdate(BaseModel):
    """
    Schema for updating an existing Tool.
    
    Why these constraints:
    - Optional fields (None): Supports 'PATCH' logic where users only send what 
      needs changing.
    - Consistency: We mirror the creation limits (200 chars) to ensure an update 
      doesn't bypass the initial security checks.
    """    
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None