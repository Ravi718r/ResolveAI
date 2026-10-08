from typing import Literal

from pydantic import BaseModel, Field


IssueType = Literal[
    "payment_failed",
    "refund_request",
    "duplicate_payment",
    "missing_order",
    "wrong_order_status",
    "cancel_order",
]


class CustomerIssue(BaseModel):

    # customer_id: int | None = Field(
    #     default=None,
    #     description="Customer ID if available"
    # )
    
    issue_type: IssueType = Field(
        description="The type of customer support issue"
    )

    order_id: int | None = Field(
        default=None,
        description="Order ID mentioned by the customer"
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence of the classification"
    )