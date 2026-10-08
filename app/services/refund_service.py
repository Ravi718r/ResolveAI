from decimal import Decimal
from datetime import datetime, timezone

from app.db.models import Refund
from app.repositories.refund import RefundRepository


class RefundService:

    def __init__(self, refund_repository: RefundRepository):
        self.refund_repository = refund_repository

    def get_refund_by_id(
        self,
        refund_id: int,
    ) -> Refund | None:
        return self.refund_repository.get_by_id(refund_id)

    def get_refund_by_payment_id(
        self,
        payment_id: int,
    ) -> Refund | None:
        return self.refund_repository.get_by_payment_id(payment_id)

    def create_refund(
        self,
        payment_id: int,
        amount: Decimal,
        reason: str,
    ) -> Refund:

        refund = Refund(
            payment_id=payment_id,
            amount=amount,
            reason=reason,
            status="pending",
            created_at=datetime.now(timezone.utc),
        )

        return self.refund_repository.create(refund)