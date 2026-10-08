from datetime import datetime

from pydantic import BaseModel, Field


class EscalationResponse(BaseModel):
    id: int
    support_case_id: int
    status: str
    reason: str
    assigned_agent: str | None
    agent_notes: str | None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None


class AssignEscalationRequest(BaseModel):
    agent: str = Field(
        min_length=1,
        max_length=100,
    )


class ResolveEscalationRequest(BaseModel):
    agent_notes: str = Field(
        min_length=1,
        max_length=2000,
    )