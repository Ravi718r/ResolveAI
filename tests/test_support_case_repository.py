from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Order, SupportCase
from app.repositories.customer import CustomerRepository
from app.repositories.order import OrderRepository
from app.repositories.support_case import SupportCaseRepository


def test_create_and_get_support_case():

    db: Session = SessionLocal()

    try:
        customer_repository = CustomerRepository(db)
        order_repository = OrderRepository(db)
        support_case_repository = SupportCaseRepository(db)

        email = "support.test@resolveai.com"

        # --------------------------------
        # 1. Get or create customer
        # --------------------------------

        customer = customer_repository.get_by_email(email)

        if customer is None:
            customer = customer_repository.create(
                name="Support Test Customer",
                email=email,
            )

        # --------------------------------
        # 2. Create order for this customer
        # --------------------------------

        order = order_repository.create(
            Order(
                customer_id=customer.id,
                amount=Decimal("1499.99"),
                currency="INR",
                status="pending",
                created_at=datetime.now(timezone.utc),
            )
        )

        # --------------------------------
        # 3. Create support case
        # --------------------------------

        support_case = support_case_repository.create(
            SupportCase(
                customer_id=customer.id,
                order_id=order.id,
                issue_type="payment_failed",
                description="Payment was deducted but order failed",
                status="open",
                resolution=None,
                created_at=datetime.now(timezone.utc),
            )
        )

        # --------------------------------
        # 4. Verify created support case
        # --------------------------------

        assert support_case.id is not None
        assert support_case.customer_id == customer.id
        assert support_case.order_id == order.id
        assert support_case.issue_type == "payment_failed"
        assert support_case.description == (
            "Payment was deducted but order failed"
        )
        assert support_case.status == "open"
        assert support_case.resolution is None

        # --------------------------------
        # 5. Get support case by ID
        # --------------------------------

        fetched = support_case_repository.get_by_id(
            support_case.id
        )

        assert fetched is not None
        assert fetched.id == support_case.id
        assert fetched.customer_id == customer.id
        assert fetched.order_id == order.id

        # --------------------------------
        # 6. Get customer's support cases
        # --------------------------------

        customer_cases = (
            support_case_repository.get_by_customer_id(
                customer.id
            )
        )

        assert any(
            case.id == support_case.id
            for case in customer_cases
        )

    finally:
        db.close()