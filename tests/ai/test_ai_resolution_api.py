from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_ai_resolution_api_valid_issue():

    fake_case = MagicMock()
    fake_case.id = 1
    fake_case.status = "resolved"
    fake_case.resolution = "Payment failure resolved."

    fake_message = (
        "Your payment failure has been resolved successfully."
    )

    # No escalation because the case was resolved automatically.
    fake_escalation = None

    with patch(
        "app.routes.ai_resolution.AIResolutionService.resolve",
        return_value=(
            fake_case,
            fake_message,
            fake_escalation,
        ),
    ):
        response = client.post(
            "/ai/resolve",
            json={
                "customer_id": 1,
                "customer_message": (
                    "My payment failed for order 123."
                ),
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["case_id"] == 1
    assert data["status"] == "resolved"
    assert data["resolution"] == "Payment failure resolved."
    assert data["message"] == fake_message
    assert data["escalated"] is False
    assert data["escalation_id"] is None
    assert data["escalation_status"] is None


def test_ai_resolution_api_pending_case_is_escalated():

    fake_case = MagicMock()
    fake_case.id = 2
    fake_case.status = "pending"
    fake_case.resolution = (
        "Manual investigation is required."
    )

    fake_message = (
        "Your issue has been escalated to a human agent."
    )

    fake_escalation = MagicMock()
    fake_escalation.id = 10
    fake_escalation.status = "open"

    with patch(
        "app.routes.ai_resolution.AIResolutionService.resolve",
        return_value=(
            fake_case,
            fake_message,
            fake_escalation,
        ),
    ):
        response = client.post(
            "/ai/resolve",
            json={
                "customer_id": 1,
                "customer_message": (
                    "My order has an issue that needs investigation."
                ),
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["case_id"] == 2
    assert data["status"] == "pending"
    assert data["resolution"] == (
        "Manual investigation is required."
    )
    assert data["message"] == fake_message

    assert data["escalated"] is True
    assert data["escalation_id"] == 10
    assert data["escalation_status"] == "open"