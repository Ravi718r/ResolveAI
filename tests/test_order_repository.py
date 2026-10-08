from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Order
from app.repositories.customer import CustomerRepository
from app.repositories.order import OrderRepository


def test_create_and_get_order():

    db: Session = SessionLocal()

    try:
        customer_repository = CustomerRepository(db)
        order_repository = OrderRepository(db)

        email = "order.test@resolveai.com"

        # Find existing customer
        customer = customer_repository.get_by_email(email)

        # Create customer if it doesn't exist
        if customer is None:
            customer = customer_repository.create(
                name="Order Test Customer",
                email=email,
            )

        # Create Order object
        order = Order(
            customer_id=customer.id,
            amount=Decimal("1499.99"),
            currency="INR",
            status="pending",
            created_at=datetime.now(timezone.utc),
        )

        # Save order through repository
        created_order = order_repository.create(order)

        # Verify created order
        assert created_order.id is not None
        assert created_order.customer_id == customer.id
        assert created_order.amount == Decimal("1499.99")
        assert created_order.currency == "INR"
        assert created_order.status == "pending"
        assert created_order.created_at is not None

        # Get order by ID
        fetched = order_repository.get_by_id(
            created_order.id,
        )

        assert fetched is not None
        assert fetched.id == created_order.id
        assert fetched.customer_id == customer.id

        # Get customer's orders
        customer_orders = order_repository.get_by_customer_id(
            customer.id,
        )

        assert any(
            existing.id == created_order.id
            for existing in customer_orders
        )

    finally:
        db.close()
