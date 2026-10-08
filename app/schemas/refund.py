from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RefundCreate(BaseModel):
    payment_id: int
    amount: Decimal
    reason: str


class RefundResponse(BaseModel):
    id: int
    payment_id: int
    amount: Decimal
    reason: str
    status: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )