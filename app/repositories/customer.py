from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Customer


class CustomerRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        name: str,
        email: str,
    ) -> Customer:

        customer = Customer(
            name=name,
            email=email,
            created_at=datetime.now(timezone.utc),
        )

        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)

        return customer

    def get_by_id(
        self,
        customer_id: int,
    ) -> Customer | None:

        return self.db.get(Customer, customer_id)

    def get_by_email(
        self,
        email: str,
    ) -> Customer | None:

        statement = select(Customer).where(
            Customer.email == email
        )

        return self.db.scalar(statement)

    def get_all(self) -> list[Customer]:

        statement = select(Customer).order_by(
            Customer.id
        )

        return list(
            self.db.scalars(statement).all()
        )

    def update(
        self,
        customer_id: int,
        name: str | None = None,
        email: str | None = None,
    ) -> Customer | None:

        customer = self.db.get(
            Customer,
            customer_id,
        )

        if customer is None:
            return None

        if name is not None:
            customer.name = name

        if email is not None:
            customer.email = email

        self.db.commit()
        self.db.refresh(customer)

        return customer

    def delete(
        self,
        customer_id: int,
    ) -> bool:

        customer = self.db.get(
            Customer,
            customer_id,
        )

        if customer is None:
            return False

        self.db.delete(customer)
        self.db.commit()

        return True