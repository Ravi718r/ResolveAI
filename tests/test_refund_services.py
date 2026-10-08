from decimal import Decimal
from unittest.mock import Mock

from app.db.models import Refund
from app.services.refund_service import RefundService


def test_get_refund_by_id():
    repository = Mock()

    refund = Refund(
        id=1,
        payment_id=10,
        amount=Decimal("500.00"),
        reason="Customer requested refund",
        status="completed",
    )

    repository.get_by_id.return_value = refund

    service = RefundService(repository)

    result = service.get_refund_by_id(1)

    assert result is refund
    repository.get_by_id.assert_called_once_with(1)


def test_get_refund_by_payment_id():
    repository = Mock()

    refund = Refund(
        id=1,
        payment_id=25,
        amount=Decimal("750.00"),
        reason="Duplicate payment",
        status="pending",
    )

    repository.get_by_payment_id.return_value = refund

    service = RefundService(repository)

    result = service.get_refund_by_payment_id(25)

    assert result is refund
    repository.get_by_payment_id.assert_called_once_with(25)


def test_create_refund():
    repository = Mock()

    created_refund = Refund(
        id=1,
        payment_id=10,
        amount=Decimal("999.99"),
        reason="Customer requested refund",
        status="pending",
    )

    repository.create.return_value = created_refund

    service = RefundService(repository)

    result = service.create_refund(
        payment_id=10,
        amount=Decimal("999.99"),
        reason="Customer requested refund",
    )

    assert result is created_refund

    repository.create.assert_called_once()

    refund_passed_to_repository = repository.create.call_args[0][0]

    assert isinstance(refund_passed_to_repository, Refund)
    assert refund_passed_to_repository.payment_id == 10
    assert refund_passed_to_repository.amount == Decimal("999.99")
    assert refund_passed_to_repository.reason == "Customer requested refund"
    assert refund_passed_to_repository.status == "pending"
    assert refund_passed_to_repository.created_at is not None