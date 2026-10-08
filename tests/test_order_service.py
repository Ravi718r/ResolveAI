from decimal import Decimal
from unittest.mock import Mock

from app.db.models import Order
from app.services.order_service import OrderService


def test_get_order_by_id():
    repository = Mock()

    order = Order(
        id=1,
        customer_id=10,
        amount=Decimal("999.99"),
        currency="INR",
        status="pending",
    )

    repository.get_by_id.return_value = order

    service = OrderService(repository)

    result = service.get_order_by_id(1)

    assert result is order
    repository.get_by_id.assert_called_once_with(1)


def test_get_orders_by_customer_id():
    repository = Mock()

    orders = [
        Order(
            id=1,
            customer_id=10,
            amount=Decimal("500.00"),
            currency="INR",
            status="paid",
        ),
        Order(
            id=2,
            customer_id=10,
            amount=Decimal("750.00"),
            currency="INR",
            status="pending",
        ),
    ]

    repository.get_by_customer_id.return_value = orders

    service = OrderService(repository)

    result = service.get_orders_by_customer_id(10)

    assert result == orders
    assert len(result) == 2

    repository.get_by_customer_id.assert_called_once_with(10)


def test_create_order():
    repository = Mock()

    created_order = Order(
        id=1,
        customer_id=10,
        amount=Decimal("999.99"),
        currency="INR",
        status="pending",
    )

    repository.create.return_value = created_order

    service = OrderService(repository)

    result = service.create_order(
        customer_id=10,
        amount=Decimal("999.99"),
        currency="INR",
        status="pending",
    )

    # Service should return the repository result
    assert result is created_order

    # Repository should be called exactly once
    repository.create.assert_called_once()

    # Get the Order object passed to repository.create()
    order_passed_to_repository = repository.create.call_args[0][0]

    # Verify the Order object
    assert isinstance(order_passed_to_repository, Order)
    assert order_passed_to_repository.customer_id == 10
    assert order_passed_to_repository.amount == Decimal("999.99")
    assert order_passed_to_repository.currency == "INR"
    assert order_passed_to_repository.status == "pending"
    assert order_passed_to_repository.created_at is not None
    
def test_update_order_status():
    repository = Mock()

    order = Order(
        id=1,
        customer_id=10,
        amount=Decimal("999.99"),
        currency="INR",
        status="pending",
    )

    repository.update.return_value = order

    service = OrderService(repository)

    result = service.update_status(
        order=order,
        status="cancelled",
    )

    assert result is order
    assert result.status == "cancelled"

    repository.update.assert_called_once_with(order)