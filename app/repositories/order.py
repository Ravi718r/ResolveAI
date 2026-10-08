from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Order


class OrderRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        order_id: int,
    ) -> Order | None:

        statement = select(Order).where(
            Order.id == order_id
        )

        return self.db.scalar(statement)

    def get_by_customer_id(
        self,
        customer_id: int,
    ) -> list[Order]:

        statement = (
            select(Order)
            .where(Order.customer_id == customer_id)
            .order_by(Order.created_at.desc())
        )

        return list(
            self.db.scalars(statement).all()
        )

    def create(
        self,
        order: Order,
    ) -> Order:

        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)

        return order

    def update(
        self,
        order: Order,
    ) -> Order:

        self.db.commit()
        self.db.refresh(order)

        return order

    def get_all(self) -> list[Order]:

        statement = (
            select(Order)
            .order_by(Order.id)
        )

        return list(
            self.db.scalars(statement).all()
        )

    def belongs_to_customer(
        self,
        order_id: int,
        customer_id: int,
    ) -> bool:
        stmt = select(Order.id).where(
            Order.id == order_id,
            Order.customer_id == customer_id,
        )
        return self.db.scalar(stmt) is not None