from decimal import Decimal
from unittest.mock import Mock

from app.db.models import Payment
from app.services.payment_service import PaymentService


def test_get_payment_by_id():
    # Arrange
    repository = Mock()
    payment = Payment(
        id=1,
        order_id=10,
        transaction_id="txn_001",
        amount=Decimal("500.00"),
        status="success",
        payment_method="upi",
    )

    repository.get_by_id.return_value = payment

    service = PaymentService(repository)

    # Act
    result = service.get_payment_by_id(1)

    # Assert
    assert result is payment
    repository.get_by_id.assert_called_once_with(1)


def test_get_payment_by_transaction_id():
    # Arrange
    repository = Mock()

    payment = Payment(
        id=1,
        order_id=10,
        transaction_id="txn_002",
        amount=Decimal("750.00"),
        status="success",
        payment_method="card",
    )

    repository.get_by_transaction_id.return_value = payment

    service = PaymentService(repository)

    # Act
    result = service.get_payment_by_transaction_id("txn_002")

    # Assert
    assert result is payment
    repository.get_by_transaction_id.assert_called_once_with("txn_002")


def test_get_payment_by_order_id():
    # Arrange
    repository = Mock()

    payment = Payment(
        id=1,
        order_id=25,
        transaction_id="txn_003",
        amount=Decimal("1000.00"),
        status="success",
        payment_method="card",
    )

    repository.get_by_order_id.return_value = payment

    service = PaymentService(repository)

    # Act
    result = service.get_payment_by_order_id(25)

    # Assert
    assert result is payment
    repository.get_by_order_id.assert_called_once_with(25)


def test_create_payment():
    # Arrange
    repository = Mock()

    created_payment = Payment(
        id=1,
        order_id=10,
        transaction_id="txn_004",
        amount=Decimal("999.99"),
        status="success",
        payment_method="upi",
    )

    repository.create.return_value = created_payment

    service = PaymentService(repository)

    # Act
    result = service.create_payment(
        order_id=10,
        transaction_id="txn_004",
        amount=Decimal("999.99"),
        status="success",
        payment_method="upi",
    )

    # Assert
    assert result is created_payment

    repository.create.assert_called_once()

    payment_passed_to_repository = repository.create.call_args[0][0]

    assert isinstance(payment_passed_to_repository, Payment)
    assert payment_passed_to_repository.order_id == 10
    assert payment_passed_to_repository.transaction_id == "txn_004"
    assert payment_passed_to_repository.amount == Decimal("999.99")
    assert payment_passed_to_repository.status == "success"
    assert payment_passed_to_repository.payment_method == "upi"
