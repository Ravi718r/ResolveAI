from app.ai.schemas import CustomerIssue
from app.db.models import Order, Payment, SupportCase
from datetime import datetime, timezone
from unittest.mock import patch


def test_ai_resolution_full_flow(client, db_session):
    # --------------------------------------------------------
    # Arrange
    # --------------------------------------------------------

    # Create an order belonging to customer 10.
    order = Order(
        id=100,
        customer_id=10,
        amount=999.99,
        currency="INR",
        status="successful",
        created_at=datetime.now(timezone.utc),
    )

    db_session.add(order)

    # Create two successful payments for the same order.
    # This represents a duplicate-payment scenario.
    payment_1 = Payment(
        order_id=100,
        transaction_id="TXN001",
        amount=999.99,
        status="successful",
        payment_method="card",
        created_at=datetime.now(timezone.utc),
    )

    payment_2 = Payment(
        order_id=100,
        transaction_id="TXN002",
        amount=999.99,
        status="successful",
        payment_method="card",
        created_at=datetime.now(timezone.utc),
    )

    db_session.add(payment_1)
    db_session.add(payment_2)

    db_session.commit()

    # --------------------------------------------------------
    # Mock only the LLM classification
    # --------------------------------------------------------

    fake_issue = CustomerIssue(
        issue_type="duplicate_payment",
        order_id=100,
        confidence=0.98,
    )

    with patch(
        "app.ai.classifier.SupportClassifier.classify",
        return_value=fake_issue,
    ):

        response = client.post(
            "/ai/resolve",
            json={
                "customer_id": 10,
                "customer_message": (
                    "I was charged twice for order 100"
                ),
            },
        )

    # --------------------------------------------------------
    # Assert HTTP response
    # --------------------------------------------------------

    assert response.status_code == 200

    data = response.json()

    assert data["case_id"] is not None
    assert data["status"] == "resolved"
    assert data["resolution"] is not None


def test_ai_pending_case_full_escalation_flow(
    client,
    db_session,
):
    """
    Full escalation lifecycle:

    Customer message
        -> AI classification
        -> SupportCase
        -> ResolutionService
        -> pending
        -> HumanEscalation(open)
        -> assign
        -> in_progress
        -> resolve
        -> resolved
        -> close
        -> closed
    """

    from unittest.mock import patch

    from app.ai.schemas import CustomerIssue

    fake_issue = CustomerIssue(
        issue_type="missing_order",
        order_id=None,
        confidence=0.98,
    )

    # ---------------------------------------------------------
    # 1. AI classifies the customer message
    # ---------------------------------------------------------

    with patch(
        "app.ai.classifier.SupportClassifier.classify",
        return_value=fake_issue,
    ):

        response = client.post(
            "/ai/resolve",
            json={
                "customer_id": 1,
                "customer_message": (
                    "My order is missing and I need help."
                ),
            },
        )

    assert response.status_code == 200

    data = response.json()

    # ---------------------------------------------------------
    # 2. AI could not automatically resolve the issue
    # ---------------------------------------------------------

    assert data["status"] == "pending"
    assert data["escalated"] is True
    assert data["escalation_id"] is not None
    assert data["escalation_status"] == "open"

    escalation_id = data["escalation_id"]

    # ---------------------------------------------------------
    # 3. Verify escalation exists through GET API
    # ---------------------------------------------------------

    response = client.get(
        f"/escalations/{escalation_id}"
    )

    assert response.status_code == 200

    escalation = response.json()

    assert escalation["id"] == escalation_id
    assert escalation["status"] == "open"
    assert escalation["assigned_agent"] is None

    # ---------------------------------------------------------
    # 4. Assign human agent
    # ---------------------------------------------------------

    response = client.patch(
        f"/escalations/{escalation_id}/assign",
        json={
            "agent": "agent_001",
        },
    )

    assert response.status_code == 200

    escalation = response.json()

    assert escalation["status"] == "in_progress"
    assert escalation["assigned_agent"] == "agent_001"

    # ---------------------------------------------------------
    # 5. Human agent resolves the issue
    # ---------------------------------------------------------

    response = client.patch(
        f"/escalations/{escalation_id}/resolve",
        json={
            "agent_notes": (
                "Customer issue investigated and resolved."
            ),
        },
    )

    assert response.status_code == 200

    escalation = response.json()

    assert escalation["status"] == "resolved"
    assert escalation["assigned_agent"] == "agent_001"
    assert escalation["agent_notes"] == (
        "Customer issue investigated and resolved."
    )
    assert escalation["resolved_at"] is not None

    # ---------------------------------------------------------
    # 6. Close escalation
    # ---------------------------------------------------------

    response = client.patch(
        f"/escalations/{escalation_id}/close"
    )

    assert response.status_code == 200

    escalation = response.json()

    assert escalation["status"] == "closed"

    # ---------------------------------------------------------
    # 7. Final database verification
    # ---------------------------------------------------------

    response = client.get(
        f"/escalations/{escalation_id}"
    )

    assert response.status_code == 200

    final_escalation = response.json()

    assert final_escalation["status"] == "closed"
    assert final_escalation["assigned_agent"] == "agent_001"