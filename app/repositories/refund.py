from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Refund


class RefundRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, refund_id: int) -> Refund | None:
        stmt = select(Refund).where(Refund.id == refund_id)
        return self.db.scalar(stmt)

    def get_by_payment_id(self, payment_id: int) -> Refund | None:
        stmt = select(Refund).where(
            Refund.payment_id == payment_id
        )
        return self.db.scalar(stmt)

    def create(self, refund: Refund) -> Refund:
        self.db.add(refund)
        self.db.commit()
        self.db.refresh(refund)

        return refund

    def update(self, refund: Refund) -> Refund:
        self.db.commit()
        self.db.refresh(refund)

        return refund

    def delete(self, refund: Refund) -> None:
        self.db.delete(refund)
        self.db.commit()