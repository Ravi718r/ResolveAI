from pydantic import BaseModel, Field


class AIResolutionRequest(BaseModel):
    customer_id: int = Field(gt=0)
    customer_message: str = Field(min_length=1)


class AIResolutionResponse(BaseModel):
    case_id: int
    status: str
    resolution: str | None
    message: str

    escalated: bool
    escalation_id: int | None
    escalation_status: str | None