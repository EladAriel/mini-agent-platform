from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field, ConfigDict, model_validator

class ModelInfo(BaseModel):
    """
    Metadata for a single supported model.

    Why this structure instead of a flat list of strings:
    - recommended_for: surfaces guidance in the API docs and lets clients
      show users which model fits their task without hardcoding that knowledge
      in the frontend.
    - is_default: a single source of truth for the fallback model — the
      executor reads this rather than hardcoding a string.
    - is_default is enforced to appear exactly once across the full list
      by the module-level validator below.
    """    
    id: str
    recommended_for: str
    is_default: bool = False

SUPPORTED_MODELS: list[ModelInfo] = [
    ModelInfo(
        id="gpt-4o",
        recommended_for="Best for complex multi-step reasoning and tool-heavy tasks.",
        is_default=True,
    ),
    ModelInfo(
        id="gpt-4o-mini",
        recommended_for="Best for fast, simple tasks where low latency matters.",
    ),
    ModelInfo(
        id="claude-3-5-sonnet",
        recommended_for="Best for writing, analysis, and nuanced instruction-following.",
    ),
    ModelInfo(
        id="claude-4-5-sonnet",
        recommended_for="Best for advanced reasoning and the most complex agent tasks.",
    ),
]

# ── Derived constants (computed once at import time) ──────────────────────────

# Flat set used for O(1) validation in RunRequest and the executor
SUPPORTED_MODEL_IDS: set[str] = {model.id for model in SUPPORTED_MODELS}

# The fallback when no model is specified — exactly one ModelInfo has is_default=True
_defaults = [model for model in SUPPORTED_MODELS if model.is_default]
assert len(_defaults) == 1, (
    f"Exactly one model must have is_default=True, found {len(_defaults)}: "
    f"{[model.id for model in _defaults]}"
)
DEFAULT_MODEL: str = _defaults[0].id


# ── Schemas ───────────────────────────────────────────────────────────────────

class RunRequest(BaseModel):
    """
    Input schema for starting an agent execution.

    Why these constraints:
    - task min_length=1: Prevents wasting LLM tokens on empty prompts.
    - task max_length=2_000: Structural guard against oversized input —
      enforced by FastAPI before the request reaches any business logic.
      Keeps length out of the guardrail, which is reserved for content
      safety checks only.
    - model defaults to DEFAULT_MODEL: callers can omit it and get a
      sensible choice without needing to know the model list.
    - model is validated against SUPPORTED_MODEL_IDS so unsupported
      strings are rejected with a clear 422 before hitting the executor.
    """
    task: str = Field(..., min_length=1, max_length=2_000)
    model: str = Field(
        default=DEFAULT_MODEL,
        description=(
            f"Model to use. Defaults to '{DEFAULT_MODEL}'. "
            f"Supported: {[m.id for m in SUPPORTED_MODELS]}"
        ),
    )

    @model_validator(mode="after")
    def validate_model(self) -> "RunRequest":
        if self.model not in SUPPORTED_MODEL_IDS:
            raise ValueError(
                f"Unsupported model '{self.model}'. "
                f"Supported: {sorted(SUPPORTED_MODEL_IDS)}"
            )
        return self

class ToolCallRecord(BaseModel):
    """
    A granular record of a single tool execution.
    
    Why this structure:
    - Storing step, input, and output allows for full transparency and 
      debugging. It lets users see exactly 'how' the agent arrived at its 
      final answer.
    """
    step: int
    tool_name: str
    tool_input: str
    tool_output: str   

class RunRead(BaseModel):
    """
    Schema for viewing a run's details in history or status updates.
    
    Why these fields:
    - final_response (Optional): Allows the schema to represent runs that 
      are still in progress or failed before completion.
    - status: Essential for the UI to distinguish between 'success', 
      'failed', or 'running'.
    - from_attributes: Enables Beanie to map the DB document directly to 
      this schema.
    """
    id: str
    agent_id: str
    model: str
    task: str
    tool_calls: list[ToolCallRecord]
    final_response: str | None = None
    steps: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)   

class RunResponse(BaseModel):
    """
    Schema returned immediately after a run completes.

    Why separate from RunRead:
    - RunRead is used for history queries (paginated list, single fetch).
    - RunResponse is returned by the executor and always contains a
      fully-populated final_response and tool trace — no Optional ambiguity.
    """
    run_id: str
    agent_id: str
    model: str
    task: str
    final_response: str
    tool_calls: list[ToolCallRecord]
    steps: int
    status: str
    created_at: datetime
    
class PaginatedRuns(BaseModel):
    """
    A wrapper for list results to support large history sets.
    
    Why this structure:
    - Including total, page, and pages allows the frontend to build 
      navigation (e.g., 'Next', 'Previous', 'Page 3 of 10') without 
      repeatedly fetching the entire database.
    """
    items: list[RunRead]
    total: int
    page: int
    page_size: int
    pages: int      