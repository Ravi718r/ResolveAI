from datetime import datetime, timezone
from decimal import Decimal

from app.db.models import Order
from app.repositories.order import OrderRepository


class OrderService:

    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    def get_order_by_id(
        self,
        order_id: int,
    ) -> Order | None:

        return self.order_repository.get_by_id(order_id)

    def get_orders_by_customer_id(
        self,
        customer_id: int,
    ) -> list[Order]:

        return self.order_repository.get_by_customer_id(
            customer_id
        )

    def create_order(
        self,
        customer_id: int,
        amount: Decimal,
        currency: str,
        status: str,
    ) -> Order:

        order = Order(
            customer_id=customer_id,
            amount=amount,
            currency=currency,
            status=status,
            created_at=datetime.now(timezone.utc),
        )

        return self.order_repository.create(order)

    def update_status(
        self,
        order: Order,
        status: str,
    ) -> Order:

        order.status = status

        return self.order_repository.update(order)


    def list_orders(self) -> list[Order]:
        return self.order_repository.get_all()