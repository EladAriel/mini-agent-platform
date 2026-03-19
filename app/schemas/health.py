from typing import Literal
from pydantic import BaseModel


class ChecksDetail(BaseModel):
    db: Literal["ok", "unavailable"]


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    checks: ChecksDetail
