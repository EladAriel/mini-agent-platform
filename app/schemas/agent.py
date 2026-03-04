from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.tool import ToolRead

class AgentCreate(BaseModel):
    """
    Schema for creating a new AI Agent.
    
    Why these constraints:
    - name: The display name (e.g., 'Research Bot'). Max 200 prevents 
      resource exhaustion and ensures the UI layout doesn't break.
    - role: The job title or persona (e.g., 'Research Assistant'). 
      Max 200 prevents malicious oversized strings from bloating 
      MongoDB storage and slowing down network requests.
    - description: The actual instructions for the agent. We leave 
      this open-ended (min_length=1) but require at least some content 
      to ensure the agent has a purpose.
    - tool_ids: A list of existing tool IDs. Defaulting to an empty 
      list ensures the agent object is always valid for iteration, 
      even if it has no tools yet.
    """    
    name: str = Field(..., min_length=1, max_length=200)
    role: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    tool_ids: list[str] = Field(default_factory=list)

class AgentRead(BaseModel):
    """
    Schema for returning Agent data, including resolved tool objects.
    
    Why from_attributes:
    - Allows Pydantic to seamlessly map from Beanie Document objects, 
      converting the database state into a clean JSON response.
    """    
    id: str
    name: str
    role: str
    description: str
    tools: list[ToolRead]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AgentUpdate(BaseModel):
    """
    Schema for partial updates to an Agent.
    
    Why these constraints:
    - Optional fields (None): Supports 'PATCH' requests.
    - tool_ids (None vs []): A value of None means 'no change', while an 
      empty list [] explicitly instructs the system to remove all tools.
    """    
    name: str | None = Field(None, min_length=1, max_length=200)
    role: str | None = None
    description: str | None = None
    tool_ids: list[str] | None = None