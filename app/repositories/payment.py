from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Payment


class PaymentRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, payment_id: int) -> Payment | None:
        stmt = select(Payment).where(Payment.id == payment_id)
        return self.db.scalar(stmt)

    def get_all_by_order_id(self, order_id: int) -> list[Payment]:
        stmt = select(Payment).where(Payment.order_id == order_id)
        return list(self.db.scalars(stmt).all())

    def get_by_transaction_id(
        self,
        transaction_id: str,
    ) -> Payment | None:
        stmt = select(Payment).where(
            Payment.transaction_id == transaction_id
        )
        return self.db.scalar(stmt)

    def get_by_order_id(self, order_id: int) -> Payment | None:
        stmt = select(Payment).where(
            Payment.order_id == order_id
        )
        return self.db.scalar(stmt)

    def create(self, payment: Payment) -> Payment:
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)

        return payment

    def update(self, payment: Payment) -> Payment:
        self.db.commit()
        self.db.refresh(payment)

        return payment

    def delete(self, payment: Payment) -> None:
        self.db.delete(payment)
        self.db.commit()