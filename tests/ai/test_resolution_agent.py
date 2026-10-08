from unittest.mock import Mock

import pytest

from app.ai.resolution_agent import AIResolutionService
from app.ai.schemas import CustomerIssue
from app.db.models import Order, SupportCase


def create_service(
    classifier,
    resolution_service,
    order_repository,
    support_case_repository,
    response_generator=None,
    escalation_service=None,
):
    if response_generator is None:
        response_generator = Mock()
        response_generator.generate.return_value = "Test response"

    if escalation_service is None:
        escalation_service = Mock()

    return AIResolutionService(
        classifier=classifier,
        resolution_service=resolution_service,
        order_repository=order_repository,
        support_case_repository=support_case_repository,
        response_generator=response_generator,
        escalation_service=escalation_service,
    )


def test_ai_resolution_valid_issue():

    classifier = Mock()
    resolution_service = Mock()
    order_repository = Mock()
    support_case_repository = Mock()
    response_generator = Mock()
    escalation_service = Mock()

    classifier.classify.return_value = CustomerIssue(
        issue_type="duplicate_payment",
        order_id=100,
        confidence=0.98,
    )

    order = Order(
        id=100,
        customer_id=10,
        amount=999.99,
        currency="INR",
        status="successful",
    )

    order_repository.get_by_id.return_value = order

    resolved_case = SupportCase(
        id=1,
        customer_id=10,
        order_id=100,
        issue_type="duplicate_payment",
        description="I was charged twice for order 100",
        status="resolved",
        resolution="Duplicate payment detected.",
    )

    support_case_repository.create.side_effect = (
        lambda case: case
    )

    resolution_service.resolve.return_value = resolved_case

    response_generator.generate.return_value = (
        "Your duplicate payment issue has been resolved."
    )

    service = create_service(
        classifier=classifier,
        resolution_service=resolution_service,
        order_repository=order_repository,
        support_case_repository=support_case_repository,
        response_generator=response_generator,
        escalation_service=escalation_service,
    )

    case, message, escalation = service.resolve(
        customer_id=10,
        customer_message="I was charged twice for order 100",
    )

    assert case is resolved_case
    assert case.status == "resolved"
    assert message == (
        "Your duplicate payment issue has been resolved."
    )
    assert escalation is None

    escalation_service.escalate.assert_not_called()

    response_generator.generate.assert_called_once()


def test_ai_resolution_rejects_order_from_another_customer():

    classifier = Mock()
    resolution_service = Mock()
    order_repository = Mock()
    support_case_repository = Mock()

    classifier.classify.return_value = CustomerIssue(
        issue_type="refund_request",
        order_id=100,
        confidence=0.98,
    )

    order = Order(
        id=100,
        customer_id=20,
        amount=999.99,
        currency="INR",
        status="completed",
    )

    order_repository.get_by_id.return_value = order

    escalation_service = Mock()
    response_generator = Mock()

    service = create_service(
        classifier=classifier,
        resolution_service=resolution_service,
        order_repository=order_repository,
        support_case_repository=support_case_repository,
        response_generator=response_generator,
        escalation_service=escalation_service,
    )

    with pytest.raises(
        ValueError,
        match="The order does not belong to this customer.",
    ):
        service.resolve(
            customer_id=10,
            customer_message="I want a refund for order 100",
        )

    support_case_repository.create.assert_not_called()
    resolution_service.resolve.assert_not_called()
    escalation_service.escalate.assert_not_called()


def test_ai_resolution_rejects_low_confidence():

    classifier = Mock()
    resolution_service = Mock()
    order_repository = Mock()
    support_case_repository = Mock()

    classifier.classify.return_value = CustomerIssue(
        issue_type="duplicate_payment",
        order_id=100,
        confidence=0.50,
    )

    service = create_service(
        classifier=classifier,
        resolution_service=resolution_service,
        order_repository=order_repository,
        support_case_repository=support_case_repository,
    )

    with pytest.raises(
        ValueError,
        match="Classification confidence is too low",
    ):
        service.resolve(
            customer_id=10,
            customer_message="Something is wrong with my payment.",
        )

    support_case_repository.create.assert_not_called()
    resolution_service.resolve.assert_not_called()


def test_ai_resolution_rejects_nonexistent_order():

    classifier = Mock()
    resolution_service = Mock()
    order_repository = Mock()
    support_case_repository = Mock()

    classifier.classify.return_value = CustomerIssue(
        issue_type="cancel_order",
        order_id=999,
        confidence=0.98,
    )

    order_repository.get_by_id.return_value = None

    service = create_service(
        classifier=classifier,
        resolution_service=resolution_service,
        order_repository=order_repository,
        support_case_repository=support_case_repository,
    )

    with pytest.raises(
        ValueError,
        match="The order mentioned by the customer could not be found.",
    ):
        service.resolve(
            customer_id=10,
            customer_message="Cancel order 999.",
        )

    support_case_repository.create.assert_not_called()
    resolution_service.resolve.assert_not_called()


def test_ai_resolution_escalates_pending_case():

    classifier = Mock()
    resolution_service = Mock()
    order_repository = Mock()
    support_case_repository = Mock()
    response_generator = Mock()
    escalation_service = Mock()

    classifier.classify.return_value = CustomerIssue(
        issue_type="missing_order",
        order_id=100,
        confidence=0.98,
    )

    order = Order(
        id=100,
        customer_id=10,
        amount=999.99,
        currency="INR",
        status="successful",
    )

    order_repository.get_by_id.return_value = order

    created_case = SupportCase(
        id=1,
        customer_id=10,
        order_id=100,
        issue_type="missing_order",
        description="My order is missing",
        status="open",
        resolution=None,
    )

    pending_case = SupportCase(
        id=1,
        customer_id=10,
        order_id=100,
        issue_type="missing_order",
        description="My order is missing",
        status="pending",
        resolution="Order requires manual investigation.",
    )

    support_case_repository.create.return_value = created_case
    resolution_service.resolve.return_value = pending_case

    fake_escalation = Mock()
    fake_escalation.id = 50
    fake_escalation.status = "open"

    escalation_service.escalate.return_value = fake_escalation

    response_generator.generate.return_value = (
        "Your issue has been escalated to a human agent."
    )

    service = create_service(
        classifier=classifier,
        resolution_service=resolution_service,
        order_repository=order_repository,
        support_case_repository=support_case_repository,
        response_generator=response_generator,
        escalation_service=escalation_service,
    )

    case, message, escalation = service.resolve(
        customer_id=10,
        customer_message="My order is missing.",
    )

    assert case is pending_case
    assert case.status == "pending"

    assert escalation is fake_escalation
    assert escalation.status == "open"

    escalation_service.escalate.assert_called_once_with(
        case=pending_case,
        reason="Order requires manual investigation.",
    )

    assert message == (
        "Your issue has been escalated to a human agent."
    )