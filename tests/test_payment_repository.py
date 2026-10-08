from decimal import Decimal
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models import Customer, Order, Payment
from app.repositories.payment import PaymentRepository


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


def test_create_and_get_payment():
    setup_database()

    db = TestingSessionLocal()

    try:
        customer = Customer(
            name="Test Customer",
            email="payment@test.com",
            created_at=datetime.now(timezone.utc),
        )

        db.add(customer)
        db.commit()
        db.refresh(customer)

        order = Order(
            customer_id=customer.id,
            amount=Decimal("999.99"),
            currency="INR",
            status="paid",
            created_at=datetime.now(timezone.utc),
        )

        db.add(order)
        db.commit()
        db.refresh(order)

        payment = Payment(
            order_id=order.id,
            transaction_id="txn_test_001",
            amount=Decimal("999.99"),
            status="success",
            payment_method="card",
            created_at=datetime.now(timezone.utc),
        )

        repository = PaymentRepository(db)

        created_payment = repository.create(payment)

        assert created_payment.id is not None
        assert created_payment.transaction_id == "txn_test_001"

        fetched_payment = repository.get_by_id(created_payment.id)

        assert fetched_payment is not None
        assert fetched_payment.id == created_payment.id
        assert fetched_payment.amount == Decimal("999.99")

    finally:
        db.close()
        teardown_database()


def test_get_payment_by_transaction_id():
    setup_database()

    db = TestingSessionLocal()

    try:
        customer = Customer(
            name="Transaction Customer",
            email="transaction@test.com",
            created_at=datetime.now(timezone.utc),
        )

        db.add(customer)
        db.commit()
        db.refresh(customer)

        order = Order(
            customer_id=customer.id,
            amount=Decimal("500.00"),
            currency="INR",
            status="paid",
            created_at=datetime.now(timezone.utc),
        )

        db.add(order)
        db.commit()
        db.refresh(order)

        payment = Payment(
            order_id=order.id,
            transaction_id="txn_test_002",
            amount=Decimal("500.00"),
            status="success",
            payment_method="upi",
            created_at=datetime.now(timezone.utc),
        )

        repository = PaymentRepository(db)
        repository.create(payment)

        result = repository.get_by_transaction_id("txn_test_002")

        assert result is not None
        assert result.transaction_id == "txn_test_002"

    finally:
        db.close()
        teardown_database()