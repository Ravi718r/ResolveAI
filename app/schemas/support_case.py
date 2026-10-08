from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SupportCaseCreate(BaseModel):
    customer_id: int
    order_id: int | None = None
    issue_type: str
    description: str

class SupportCaseResolve(BaseModel):
    resolution: str
    
class SupportCaseResponse(BaseModel):
    id: int
    customer_id: int
    order_id: int | None
    issue_type: str
    description: str
    status: str
    resolution: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)