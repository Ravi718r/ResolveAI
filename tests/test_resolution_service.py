from decimal import Decimal
from unittest.mock import Mock

from app.db.models import Order, Refund, Payment, SupportCase
from app.services.resolution_service import ResolutionService


# ============================================================
# 1. PAYMENT FAILED
# ============================================================

def test_resolve_failed_payment():
    # Mock repositories so this test does not require a real database.
    support_case_repository = Mock()
    order_repository = Mock()
    payment_repository = Mock()
    refund_repository = Mock()

    case = SupportCase(
        id=1,
        customer_id=10,
        order_id=100,
        issue_type="payment_failed",
        description="Payment failed",
        status="open",
        resolution=None,
    )

    order = Order(
        id=100,
        customer_id=10,
        amount=Decimal("999.99"),
        currency="INR",
        status="failed",
    )

    payment = Payment(
        id=1,
        order_id=100,
        transaction_id="TXN123",
        amount=Decimal("999.99"),
        status="failed",
        payment_method="upi",
    )

    # Tell the mocks what the repositories should return.
    order_repository.get_by_id.return_value = order
    payment_repository.get_by_order_id.return_value = payment

    # Instead of actually committing to DB, simply return the modified case.
    support_case_repository.update.side_effect = lambda case: case

    service = ResolutionService(
        support_case_repository=support_case_repository,
        order_repository=order_repository,
        payment_repository=payment_repository,
        refund_repository=refund_repository,
    )

    result = service.resolve_payment_failed(case)

    assert result.status == "resolved"
    assert result.resolution is not None

    # Verify repositories were called correctly.
    order_repository.get_by_id.assert_called_once_with(100)
    payment_repository.get_by_order_id.assert_called_once_with(100)


# ============================================================
# 2. REFUND REQUEST
# ============================================================

def test_resolve_refund_request():
    support_case_repository = Mock()
    order_repository = Mock()
    payment_repository = Mock()
    refund_repository = Mock()

    case = SupportCase(
        id=2,
        customer_id=10,
        order_id=100,
        issue_type="refund_request",
        description="I want a refund",
        status="open",
        resolution=None,
    )

    order = Order(
        id=100,
        customer_id=10,
        amount=Decimal("999.99"),
        currency="INR",
        status="completed",
    )

    payment = Payment(
        id=1,
        order_id=100,
        transaction_id="TXN456",
        amount=Decimal("999.99"),
        status="successful",
        payment_method="upi",
    )

    order_repository.get_by_id.return_value = order
    payment_repository.get_by_order_id.return_value = payment

    # IMPORTANT:
    # None means there is NO existing refund.
    # Without this, Mock would return another Mock object and
    # the service could incorrectly think a refund already exists.
    refund_repository.get_by_payment_id.return_value = None

    support_case_repository.update.side_effect = lambda case: case

    service = ResolutionService(
        support_case_repository=support_case_repository,
        order_repository=order_repository,
        payment_repository=payment_repository,
        refund_repository=refund_repository,
    )

    result = service.resolve_refund_request(case)

    assert result.status == "resolved"
    assert result.resolution is not None

    # A new refund should have been created.
    refund_repository.create.assert_called_once()

    # Get the Refund object passed to repository.create()
    created_refund = refund_repository.create.call_args.args[0]

    assert created_refund.payment_id == payment.id
    assert created_refund.amount == payment.amount
    assert created_refund.status == "pending"


# ============================================================
# 3. DUPLICATE PAYMENT
# ============================================================

def test_resolve_duplicate_payment():
    support_case_repository = Mock()
    order_repository = Mock()
    payment_repository = Mock()
    refund_repository = Mock()

    case = SupportCase(
        id=1,
        customer_id=10,
        order_id=100,
        issue_type="duplicate_payment",
        description="I was charged twice for the same order",
        status="open",
        resolution=None,
    )

    order = Order(
        id=100,
        customer_id=10,
        amount=Decimal("999.99"),
        currency="INR",
        status="successful",
    )

    payment_1 = Payment(
        id=1,
        order_id=100,
        transaction_id="TXN123",
        amount=Decimal("999.99"),
        status="successful",
        payment_method="upi",
    )

    payment_2 = Payment(
        id=2,
        order_id=100,
        transaction_id="TXN124",
        amount=Decimal("999.99"),
        status="successful",
        payment_method="upi",
    )

    order_repository.get_by_id.return_value = order

    # Two successful payments = duplicate payment.
    payment_repository.get_all_by_order_id.return_value = [
        payment_1,
        payment_2,
    ]

    support_case_repository.update.side_effect = lambda case: case

    service = ResolutionService(
        support_case_repository=support_case_repository,
        order_repository=order_repository,
        payment_repository=payment_repository,
        refund_repository=refund_repository,
    )

    result = service.resolve_duplicate_payment(case)

    assert result.status == "resolved"
    assert result.resolution is not None

    # Match the actual resolution message from the service.
    assert "Duplicate successful payment detected" in result.resolution

    order_repository.get_by_id.assert_called_once_with(100)
    payment_repository.get_all_by_order_id.assert_called_once_with(100)
    support_case_repository.update.assert_called_once_with(case)


# ============================================================
# 4. MISSING ORDER
# ============================================================

def test_resolve_missing_order():
    support_case_repository = Mock()
    order_repository = Mock()
    payment_repository = Mock()
    refund_repository = Mock()

    case = SupportCase(
        id=1,
        customer_id=10,
        order_id=100,
        issue_type="missing_order",
        description="My order is missing",
        status="open",
        resolution=None,
    )

    # Order does not exist.
    order_repository.get_by_id.return_value = None

    support_case_repository.update.side_effect = lambda case: case

    service = ResolutionService(
        support_case_repository=support_case_repository,
        order_repository=order_repository,
        payment_repository=payment_repository,
        refund_repository=refund_repository,
    )

    result = service.resolve_missing_order(case)

    # Missing order cannot be automatically resolved.
    assert result.status == "pending"
    assert result.resolution is not None
    assert "could not be found" in result.resolution

    order_repository.get_by_id.assert_called_once_with(100)
    support_case_repository.update.assert_called_once_with(case)


# ============================================================
# 5. WRONG ORDER STATUS
# ============================================================

def test_resolve_wrong_order_status():
    support_case_repository = Mock()
    order_repository = Mock()
    payment_repository = Mock()
    refund_repository = Mock()

    case = SupportCase(
        id=1,
        customer_id=10,
        order_id=100,
        issue_type="wrong_order_status",
        description="My order status is incorrect",
        status="open",
        resolution=None,
    )

    order = Order(
        id=100,
        customer_id=10,
        amount=Decimal("999.99"),
        currency="INR",
        status="something_wrong",
    )

    order_repository.get_by_id.return_value = order

    support_case_repository.update.side_effect = lambda case: case

    service = ResolutionService(
        support_case_repository=support_case_repository,
        order_repository=order_repository,
        payment_repository=payment_repository,
        refund_repository=refund_repository,
    )

    result = service.resolve_wrong_order_status(case)

    # Invalid status requires manual investigation.
    assert result.status == "pending"
    assert result.resolution is not None
    assert "Invalid order status" in result.resolution

    order_repository.get_by_id.assert_called_once_with(100)
    support_case_repository.update.assert_called_once_with(case)


# ============================================================
# 6. VALID ORDER STATUS
# ============================================================

def test_resolve_wrong_order_status_when_status_is_valid():
    support_case_repository = Mock()
    order_repository = Mock()
    payment_repository = Mock()
    refund_repository = Mock()

    case = SupportCase(
        id=1,
        customer_id=10,
        order_id=100,
        issue_type="wrong_order_status",
        description="My order status is incorrect",
        status="open",
        resolution=None,
    )

    order = Order(
        id=100,
        customer_id=10,
        amount=Decimal("999.99"),
        currency="INR",
        status="successful",
    )

    order_repository.get_by_id.return_value = order

    support_case_repository.update.side_effect = lambda case: case

    service = ResolutionService(
        support_case_repository=support_case_repository,
        order_repository=order_repository,
        payment_repository=payment_repository,
        refund_repository=refund_repository,
    )

    result = service.resolve_wrong_order_status(case)

    # Valid status does not mean we know how to fix the complaint.
    # Therefore it remains pending for manual investigation.
    assert result.status == "pending"
    assert result.resolution is not None
    assert "is valid" in result.resolution

    order_repository.get_by_id.assert_called_once_with(100)
    support_case_repository.update.assert_called_once_with(case)


# ============================================================
# 7. CANCEL ORDER - SUCCESS
# ============================================================

def test_resolve_cancel_order():
    support_case_repository = Mock()
    order_repository = Mock()
    payment_repository = Mock()
    refund_repository = Mock()

    case = SupportCase(
        id=1,
        customer_id=10,
        order_id=100,
        issue_type="cancel_order",
        description="I want to cancel my order",
        status="open",
        resolution=None,
    )

    order = Order(
        id=100,
        customer_id=10,
        amount=Decimal("999.99"),
        currency="INR",
        status="pending",
    )

    order_repository.get_by_id.return_value = order
    support_case_repository.update.side_effect = lambda case: case

    service = ResolutionService(
        support_case_repository=support_case_repository,
        order_repository=order_repository,
        payment_repository=payment_repository,
        refund_repository=refund_repository,
    )

    result = service.resolve_cancel_order(case)

    assert result.status == "resolved"
    assert result.resolution is not None
    assert "successfully cancelled" in result.resolution

    # Pending order should now be cancelled.
    assert order.status == "cancelled"

    order_repository.get_by_id.assert_called_once_with(100)
    order_repository.update.assert_called_once_with(order)
    support_case_repository.update.assert_called_once_with(case)


# ============================================================
# 8. CANCEL ORDER - SUCCESSFUL ORDER
# ============================================================

def test_resolve_cancel_order_when_order_is_successful():
    support_case_repository = Mock()
    order_repository = Mock()
    payment_repository = Mock()
    refund_repository = Mock()

    case = SupportCase(
        id=1,
        customer_id=10,
        order_id=100,
        issue_type="cancel_order",
        description="I want to cancel my order",
        status="open",
        resolution=None,
    )

    order = Order(
        id=100,
        customer_id=10,
        amount=Decimal("999.99"),
        currency="INR",
        status="successful",
    )

    order_repository.get_by_id.return_value = order
    support_case_repository.update.side_effect = lambda case: case

    service = ResolutionService(
        support_case_repository=support_case_repository,
        order_repository=order_repository,
        payment_repository=payment_repository,
        refund_repository=refund_repository,
    )

    result = service.resolve_cancel_order(case)

    # Successful orders cannot be automatically cancelled.
    assert result.status == "pending"
    assert result.resolution is not None
    assert "cannot be automatically cancelled" in result.resolution

    # Make sure we didn't accidentally change the order.
    assert order.status == "successful"

    order_repository.get_by_id.assert_called_once_with(100)
    order_repository.update.assert_not_called()
    support_case_repository.update.assert_called_once_with(case)


# ============================================================
# 9. DUPLICATE PAYMENT - FAILED PAYMENT SHOULD NOT COUNT
# ============================================================

def test_duplicate_payment_ignores_failed_payment():
    support_case_repository = Mock()
    order_repository = Mock()
    payment_repository = Mock()
    refund_repository = Mock()

    case = SupportCase(
        id=1,
        customer_id=10,
        order_id=100,
        issue_type="duplicate_payment",
        description="I was charged twice",
        status="open",
        resolution=None,
    )

    order = Order(
        id=100,
        customer_id=10,
        amount=Decimal("999.99"),
        currency="INR",
        status="successful",
    )

    successful_payment = Payment(
        id=1,
        order_id=100,
        transaction_id="TXN1",
        amount=Decimal("999.99"),
        status="successful",
        payment_method="upi",
    )

    failed_payment = Payment(
        id=2,
        order_id=100,
        transaction_id="TXN2",
        amount=Decimal("999.99"),
        status="failed",
        payment_method="upi",
    )

    order_repository.get_by_id.return_value = order

    # One successful + one failed payment.
    # This is NOT a duplicate successful payment.
    payment_repository.get_all_by_order_id.return_value = [
        successful_payment,
        failed_payment,
    ]

    support_case_repository.update.side_effect = lambda case: case

    service = ResolutionService(
        support_case_repository,
        order_repository,
        payment_repository,
        refund_repository,
    )

    result = service.resolve_duplicate_payment(case)

    assert result.status == "pending"
    assert "No duplicate successful payment" in result.resolution


# ============================================================
# 10. REFUND REQUEST - DUPLICATE REFUND
# ============================================================

def test_refund_request_does_not_create_duplicate_refund():
    support_case_repository = Mock()
    order_repository = Mock()
    payment_repository = Mock()
    refund_repository = Mock()

    case = SupportCase(
        id=1,
        customer_id=10,
        order_id=100,
        issue_type="refund_request",
        description="I want a refund",
        status="open",
        resolution=None,
    )

    order = Order(
        id=100,
        customer_id=10,
        amount=Decimal("999.99"),
        currency="INR",
        status="completed",
    )

    payment = Payment(
        id=1,
        order_id=100,
        transaction_id="TXN1",
        amount=Decimal("999.99"),
        status="successful",
        payment_method="upi",
    )

    # Existing refund already exists for this payment.
    existing_refund = Refund(
        id=1,
        payment_id=1,
        amount=Decimal("999.99"),
        reason="Customer requested refund",
        status="pending",
    )

    order_repository.get_by_id.return_value = order
    payment_repository.get_by_order_id.return_value = payment

    # Tell the service that a refund already exists.
    refund_repository.get_by_payment_id.return_value = existing_refund

    support_case_repository.update.side_effect = lambda case: case

    service = ResolutionService(
        support_case_repository,
        order_repository,
        payment_repository,
        refund_repository,
    )

    result = service.resolve_refund_request(case)

    # Existing refund means we should NOT create another one.
    assert result.status == "pending"
    assert "refund already exists" in result.resolution

    refund_repository.create.assert_not_called()


# ============================================================
# 11. SECURITY - ORDER BELONGS TO DIFFERENT CUSTOMER
# ============================================================

def test_resolution_rejects_order_belonging_to_another_customer():
    support_case_repository = Mock()
    order_repository = Mock()
    payment_repository = Mock()
    refund_repository = Mock()

    case = SupportCase(
        id=1,
        customer_id=10,
        order_id=100,
        issue_type="cancel_order",
        description="Cancel my order",
        status="open",
        resolution=None,
    )

    # IMPORTANT:
    # The order belongs to customer 20,
    # but the support case belongs to customer 10.
    order = Order(
        id=100,
        customer_id=20,
        amount=Decimal("999.99"),
        currency="INR",
        status="pending",
    )

    order_repository.get_by_id.return_value = order
    support_case_repository.update.side_effect = lambda case: case

    service = ResolutionService(
        support_case_repository,
        order_repository,
        payment_repository,
        refund_repository,
    )

    result = service.resolve_cancel_order(case)

    # The service must reject this request.
    assert result.status == "pending"
    assert "does not belong to the customer" in result.resolution

    # Most importantly, the order must NOT be modified.
    order_repository.update.assert_not_called()


# ============================================================
# 12. CANCEL ORDER - NO ORDER ID
# ============================================================

def test_cancel_order_with_no_order_id():
    support_case_repository = Mock()
    order_repository = Mock()
    payment_repository = Mock()
    refund_repository = Mock()

    case = SupportCase(
        id=1,
        customer_id=10,
        order_id=None,
        issue_type="cancel_order",
        description="Cancel my order",
        status="open",
        resolution=None,
    )

    support_case_repository.update.side_effect = lambda case: case

    service = ResolutionService(
        support_case_repository,
        order_repository,
        payment_repository,
        refund_repository,
    )

    result = service.resolve_cancel_order(case)

    # No order means there is nothing to cancel.
    assert result.status == "pending"
    assert "No order is associated" in result.resolution

    # Since there is no order_id, repository should never be called.
    order_repository.get_by_id.assert_not_called()
    order_repository.update.assert_not_called()


def test_resolve_accepts_payment_failure_alias():
    """
    Different wording should map to the same
    payment_failed business rule.
    """

    support_case_repository = Mock()
    order_repository = Mock()
    payment_repository = Mock()
    refund_repository = Mock()

    case = SupportCase(
        id=20,
        customer_id=10,
        order_id=100,
        issue_type="failed payment",
        description="My payment failed",
        status="open",
        resolution=None,
    )

    order = Order(
        id=100,
        customer_id=10,
        amount=Decimal("999.99"),
        currency="INR",
        status="failed",
    )

    payment = Payment(
        id=20,
        order_id=100,
        transaction_id="TXN-ALIAS",
        amount=Decimal("999.99"),
        status="failed",
        payment_method="upi",
    )

    order_repository.get_by_id.return_value = order
    payment_repository.get_by_order_id.return_value = payment

    support_case_repository.update.side_effect = lambda case: case

    service = ResolutionService(
        support_case_repository,
        order_repository,
        payment_repository,
        refund_repository,
    )

    result = service.resolve(case)

    assert result.status == "resolved"
    assert result.resolution is not None

def test_resolve_unknown_issue_type_goes_to_pending():
    """
    Unknown issue types must never trigger a business rule.
    """

    support_case_repository = Mock()
    order_repository = Mock()
    payment_repository = Mock()
    refund_repository = Mock()

    case = SupportCase(
        id=21,
        customer_id=10,
        order_id=100,
        issue_type="paymant failure",  # Intentional typo
        description="My payment failed",
        status="open",
        resolution=None,
    )

    support_case_repository.update.side_effect = lambda case: case

    service = ResolutionService(
        support_case_repository,
        order_repository,
        payment_repository,
        refund_repository,
    )

    result = service.resolve(case)

    assert result.status == "pending"
    assert "Unsupported issue type" in result.resolution

    # No business operation should have been triggered.
    order_repository.get_by_id.assert_not_called()
    payment_repository.get_by_order_id.assert_not_called()
