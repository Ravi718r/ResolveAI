from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PaymentCreate(BaseModel):
    order_id: int
    transaction_id: str
    amount: Decimal
    status: str
    payment_method: str


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    transaction_id: str
    amount: Decimal
    status: str
    payment_method: str

    model_config = ConfigDict(from_attributes=True)