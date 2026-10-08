from decimal import Decimal
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models import Customer, Order, Payment, Refund
from app.repositories.refund import RefundRepository


DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def setup_database():
    Base.metadata.create_all(bind=engine)


def teardown_database():
    Base.metadata.drop_all(bind=engine)


def test_create_and_get_refund():
    setup_database()

    db = TestingSessionLocal()

    try:
        customer = Customer(
            name="Refund Customer",
            email="refund@test.com",
            created_at=datetime.now(timezone.utc),
        )

        db.add(customer)
        db.commit()
        db.refresh(customer)

        order = Order(
            customer_id=customer.id,
            amount=Decimal("1000.00"),
            currency="INR",
            status="paid",
            created_at=datetime.now(timezone.utc),
        )

        db.add(order)
        db.commit()
        db.refresh(order)

        payment = Payment(
            order_id=order.id,
            transaction_id="txn_refund_001",
            amount=Decimal("1000.00"),
            status="success",
            payment_method="card",
            created_at=datetime.now(timezone.utc),
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)

        refund = Refund(
            payment_id=payment.id,
            amount=Decimal("1000.00"),
            reason="Customer requested refund",
            status="pending",
            created_at=datetime.now(timezone.utc),
        )

        repository = RefundRepository(db)

        created_refund = repository.create(refund)

        assert created_refund.id is not None
        assert created_refund.amount == Decimal("1000.00")

        fetched_refund = repository.get_by_id(created_refund.id)

        assert fetched_refund is not None
        assert fetched_refund.id == created_refund.id
        assert fetched_refund.reason == "Customer requested refund"

    finally:
        db.close()
        teardown_database()


def test_get_refund_by_payment_id():
    setup_database()

    db = TestingSessionLocal()

    try:
        customer = Customer(
            name="Payment Refund Customer",
            email="paymentrefund@test.com",
            created_at=datetime.now(timezone.utc),
        )

        db.add(customer)
        db.commit()
        db.refresh(customer)

        order = Order(
            customer_id=customer.id,
            amount=Decimal("750.00"),
            currency="INR",
            status="paid",
            created_at=datetime.now(timezone.utc),
        )

        db.add(order)
        db.commit()
        db.refresh(order)

        payment = Payment(
            order_id=order.id,
            transaction_id="txn_refund_002",
            amount=Decimal("750.00"),
            status="success",
            payment_method="upi",
            created_at=datetime.now(timezone.utc),
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)

        refund = Refund(
            payment_id=payment.id,
            amount=Decimal("750.00"),
            reason="Duplicate payment",
            status="completed",
            created_at=datetime.now(timezone.utc),
        )

        repository = RefundRepository(db)
        repository.create(refund)

        result = repository.get_by_payment_id(payment.id)

        assert result is not None
        assert result.payment_id == payment.id
        assert result.status == "completed"

    finally:
        db.close()
        teardown_database()