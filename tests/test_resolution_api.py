from decimal import Decimal
from datetime import datetime, timezone
from app.db.models import Customer, Order, Payment, SupportCase


# ============================================================
# Helper
# ============================================================

def create_customer(db, customer_id: int = 1) -> Customer:
    """
    Create a customer for the API test.

    created_at is required by the Customer model,
    so we explicitly provide the current UTC time.
    """

    customer = Customer(
        id=customer_id,
        name="Test Customer",
        email=f"customer{customer_id}@test.com",

        # Customer.created_at is NOT NULL,
        # so the test must provide a value.
        created_at=datetime.now(timezone.utc),
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer

# ============================================================
# 1. CASE NOT FOUND
# ============================================================

def test_resolution_case_not_found(client):
    """
    If the requested support case doesn't exist,
    the API should return HTTP 404.
    """

    response = client.post(
        "/resolution/resolve",
        json={"case_id": 9999},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Support case not found"
    }


# ============================================================
# 2. PAYMENT FAILED
# ============================================================

def test_resolution_payment_failed(client, db_session):
    """
    A failed payment should be automatically resolved.
    """

    # Create required customer.
    create_customer(db_session, customer_id=1)

    # Create order.
    order = Order(
        customer_id=1,
        amount=Decimal("999.99"),
        currency="INR",
        status="failed",
        created_at=datetime.now(timezone.utc),
    )

    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)

    # Create failed payment.
    payment = Payment(
        order_id=order.id,
        transaction_id="TEST-TXN-001",
        amount=Decimal("999.99"),
        status="failed",
        payment_method="upi",
        created_at=datetime.now(timezone.utc),
    )

    db_session.add(payment)

    # Create support case.
    case = SupportCase(
        customer_id=1,
        order_id=order.id,
        issue_type="payment_failed",
        description="My payment failed",
        status="open",
        resolution=None,
        created_at=datetime.now(timezone.utc),
    )

    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    # Call API.
    response = client.post(
        "/resolution/resolve",
        json={"case_id": case.id},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["case_id"] == case.id
    assert data["status"] == "resolved"
    assert data["resolution"] is not None


# ============================================================
# 3. CANCEL ORDER
# ============================================================

def test_resolution_cancel_order(client, db_session):
    """
    A pending order should be automatically cancelled.
    """

    create_customer(db_session, customer_id=2)

    order = Order(
        customer_id=2,
        amount=Decimal("500.00"),
        currency="INR",
        status="pending",
        created_at=datetime.now(timezone.utc),
    )

    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)

    case = SupportCase(
        customer_id=2,
        order_id=order.id,
        issue_type="cancel_order",
        description="Please cancel my order",
        status="open",
        resolution=None,
        created_at=datetime.now(timezone.utc),
    )

    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    response = client.post(
        "/resolution/resolve",
        json={"case_id": case.id},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["case_id"] == case.id
    assert data["status"] == "resolved"

    # Refresh order from database and verify that
    # the actual database value changed.
    db_session.refresh(order)

    assert order.status == "cancelled"


# ============================================================
# 4. UNSUPPORTED ISSUE TYPE
# ============================================================

def test_resolution_unsupported_issue_type(client, db_session):
    """
    Unknown issue types should never trigger a business action.
    They should remain pending for manual investigation.
    """

    create_customer(db_session, customer_id=3)

    case = SupportCase(
        customer_id=3,
        order_id=None,
        issue_type="something_random",
        description="Something is wrong",
        status="open",
        resolution=None,
        created_at=datetime.now(timezone.utc),
    )

    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    response = client.post(
        "/resolution/resolve",
        json={"case_id": case.id},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["case_id"] == case.id
    assert data["status"] == "pending"
    assert "Unsupported issue type" in data["resolution"]

# ============================================================
# 5. REFUND REQUEST
# ============================================================

def test_resolution_refund_request(client, db_session):
    """
    A refund request for a successful payment should
    create a refund and resolve the support case.
    """

    # Create customer.
    create_customer(db_session, customer_id=4)

    # Create completed order.
    order = Order(
        customer_id=4,
        amount=Decimal("1200.00"),
        currency="INR",
        status="completed",
        created_at=datetime.now(timezone.utc),
    )

    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)

    # Create successful payment.
    payment = Payment(
        order_id=order.id,
        transaction_id="TEST-TXN-REFUND-001",
        amount=Decimal("1200.00"),
        status="successful",
        payment_method="upi",
        created_at=datetime.now(timezone.utc),
    )

    db_session.add(payment)
    db_session.commit()
    db_session.refresh(payment)

    # Create refund request case.
    case = SupportCase(
        customer_id=4,
        order_id=order.id,
        issue_type="refund_request",
        description="I want a refund for my order",
        status="open",
        resolution=None,
        created_at=datetime.now(timezone.utc),
    )

    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    # Call API.
    response = client.post(
        "/resolution/resolve",
        json={"case_id": case.id},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["case_id"] == case.id
    assert data["status"] == "resolved"
    assert data["resolution"] is not None

# ============================================================
# 6. DUPLICATE PAYMENT
# ============================================================

def test_resolution_duplicate_payment(client, db_session):
    """
    Two successful payments for the same order should be
    detected as a duplicate payment.
    """

    # Create customer.
    create_customer(db_session, customer_id=5)

    # Create order.
    order = Order(
        customer_id=5,
        amount=Decimal("1500.00"),
        currency="INR",
        status="completed",
        created_at=datetime.now(timezone.utc),
    )

    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)

    # First successful payment.
    payment_1 = Payment(
        order_id=order.id,
        transaction_id="TEST-TXN-DUP-001",
        amount=Decimal("1500.00"),
        status="successful",
        payment_method="upi",
        created_at=datetime.now(timezone.utc),
    )

    # Second successful payment.
    payment_2 = Payment(
        order_id=order.id,
        transaction_id="TEST-TXN-DUP-002",
        amount=Decimal("1500.00"),
        status="successful",
        payment_method="upi",
        created_at=datetime.now(timezone.utc),
    )

    db_session.add_all([payment_1, payment_2])
    db_session.commit()

    # Create support case.
    case = SupportCase(
        customer_id=5,
        order_id=order.id,
        issue_type="duplicate_payment",
        description="I was charged twice for the same order",
        status="open",
        resolution=None,
        created_at=datetime.now(timezone.utc),
    )

    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    # Call API.
    response = client.post(
        "/resolution/resolve",
        json={"case_id": case.id},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["case_id"] == case.id
    assert data["status"] == "resolved"
    assert data["resolution"] is not None
    assert "Duplicate successful payment detected" in data["resolution"]

# ============================================================
# 7. MISSING ORDER
# ============================================================

def test_resolution_missing_order(client, db_session):
    """
    A support case referencing a non-existent order should
    remain pending for manual investigation.
    """

    # Create customer.
    create_customer(db_session, customer_id=6)

    # Create support case with an order ID that does not exist.
    case = SupportCase(
        customer_id=6,
        order_id=99999,
        issue_type="missing_order",
        description="My order is missing",
        status="open",
        resolution=None,
        created_at=datetime.now(timezone.utc),
    )

    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    # Call API.
    response = client.post(
        "/resolution/resolve",
        json={"case_id": case.id},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["case_id"] == case.id
    assert data["status"] == "pending"
    assert data["resolution"] is not None
    assert "could not be found" in data["resolution"]

# ============================================================
# 8. WRONG ORDER STATUS
# ============================================================

def test_resolution_wrong_order_status(client, db_session):
    """
    An invalid order status should not trigger an automatic
    business action. The case should remain pending.
    """

    # Create customer.
    create_customer(db_session, customer_id=7)

    # Create order with an invalid status.
    order = Order(
        customer_id=7,
        amount=Decimal("800.00"),
        currency="INR",
        status="unknown_status",
        created_at=datetime.now(timezone.utc),
    )

    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)

    # Create support case.
    case = SupportCase(
        customer_id=7,
        order_id=order.id,
        issue_type="wrong_order_status",
        description="My order status is showing incorrectly",
        status="open",
        resolution=None,
        created_at=datetime.now(timezone.utc),
    )

    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    # Call API.
    response = client.post(
        "/resolution/resolve",
        json={"case_id": case.id},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["case_id"] == case.id
    assert data["status"] == "pending"
    assert data["resolution"] is not None
    assert "Invalid order status" in data["resolution"]

# ============================================================
# 9. ORDER OWNERSHIP MISMATCH
# ============================================================

def test_resolution_order_belongs_to_another_customer(
    client,
    db_session,
):
    """
    A support case must not operate on an order that belongs
    to another customer.
    """

    # Create two customers.
    create_customer(db_session, customer_id=8)
    create_customer(db_session, customer_id=9)

    # Create order belonging to customer 9.
    order = Order(
        customer_id=9,
        amount=Decimal("1000.00"),
        currency="INR",
        status="pending",
        created_at=datetime.now(timezone.utc),
    )

    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)

    # Create support case belonging to customer 8,
    # but referencing customer 9's order.
    case = SupportCase(
        customer_id=8,
        order_id=order.id,
        issue_type="cancel_order",
        description="Please cancel my order",
        status="open",
        resolution=None,
        created_at=datetime.now(timezone.utc),
    )

    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    # Call API.
    response = client.post(
        "/resolution/resolve",
        json={"case_id": case.id},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["case_id"] == case.id
    assert data["status"] == "pending"
    assert data["resolution"] is not None
    assert "does not belong to the customer" in data["resolution"]

    # Most importantly, the order must NOT be cancelled.
    db_session.refresh(order)

    assert order.status == "pending"


# ============================================================
# 10. CANCEL SUCCESSFUL ORDER
# ============================================================

def test_resolution_cancel_successful_order(client, db_session):
    """
    A successful/completed order must not be automatically
    cancelled. The case should remain pending.
    """

    # Create customer.
    create_customer(db_session, customer_id=10)

    # Create completed order.
    order = Order(
        customer_id=10,
        amount=Decimal("2000.00"),
        currency="INR",
        status="completed",
        created_at=datetime.now(timezone.utc),
    )

    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)

    # Create cancellation request.
    case = SupportCase(
        customer_id=10,
        order_id=order.id,
        issue_type="cancel_order",
        description="Please cancel my completed order",
        status="open",
        resolution=None,
        created_at=datetime.now(timezone.utc),
    )

    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    # Call API.
    response = client.post(
        "/resolution/resolve",
        json={"case_id": case.id},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["case_id"] == case.id
    assert data["status"] == "pending"
    assert data["resolution"] is not None
    assert "cannot be automatically cancelled" in data["resolution"]

    # Verify the actual order was NOT changed.
    db_session.refresh(order)

    assert order.status == "completed"

# ============================================================
# 11. ALREADY RESOLVED CASE
# ============================================================

def test_resolution_already_resolved_case(client, db_session):
    """
    An already resolved support case should not be processed
    again.
    """

    create_customer(db_session, customer_id=11)

    order = Order(
        customer_id=11,
        amount=Decimal("750.00"),
        currency="INR",
        status="pending",
        created_at=datetime.now(timezone.utc),
    )

    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)

    case = SupportCase(
        customer_id=11,
        order_id=order.id,
        issue_type="cancel_order",
        description="Cancel my order",
        status="resolved",
        resolution="Already cancelled by support.",
        created_at=datetime.now(timezone.utc),
    )

    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    response = client.post(
        "/resolution/resolve",
        json={"case_id": case.id},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["case_id"] == case.id
    assert data["status"] == "resolved"
    assert data["resolution"] == "Already cancelled by support."

    # The order must remain unchanged because the case
    # was already resolved.
    db_session.refresh(order)

    assert order.status == "pending"