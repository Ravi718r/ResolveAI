from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class OrderCreate(BaseModel):
    customer_id: int
    amount: Decimal
    currency: str
    status: str


class OrderResponse(BaseModel):
    id: int
    customer_id: int
    amount: Decimal
    currency: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
