from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from app.db.models import HumanEscalation, SupportCase
from app.services.human_escalation_service import (
    HumanEscalationService,
)


def create_case() -> SupportCase:
    return SupportCase(
        id=1,
        customer_id=100,
        order_id=500,
        issue_type="refund_request",
        description="I want a refund",
        status="pending",
        resolution="Manual investigation required.",
    )


def create_escalation() -> HumanEscalation:
    now = datetime.now(UTC)

    return HumanEscalation(
        id=1,
        support_case_id=1,
        status="open",
        reason="Automatic resolution was not possible.",
        assigned_agent=None,
        agent_notes=None,
        created_at=now,
        updated_at=now,
        resolved_at=None,
    )


def test_escalate_creates_new_escalation():
    repository = Mock()
    service = HumanEscalationService(repository)

    case = create_case()

    repository.get_by_case_id.return_value = None

    def create_side_effect(escalation):
        return escalation

    repository.create.side_effect = create_side_effect

    result = service.escalate(
        case=case,
        reason="Manual investigation required.",
    )

    assert result.status == "open"
    assert result.support_case_id == case.id
    assert result.reason == "Manual investigation required."
    assert result.assigned_agent is None
    assert result.agent_notes is None
    assert result.resolved_at is None

    repository.get_by_case_id.assert_called_once_with(case.id)
    repository.create.assert_called_once()

def test_duplicate_escalation_returns_existing():
    repository = Mock()
    service = HumanEscalationService(repository)

    case = create_case()
    existing = create_escalation()

    repository.get_by_case_id.return_value = existing

    result = service.escalate(
        case=case,
        reason="Another reason",
    )

    assert result is existing

    repository.get_by_case_id.assert_called_once_with(case.id)
    repository.create.assert_not_called()


def test_assign_moves_escalation_to_in_progress():
    repository = Mock()
    service = HumanEscalationService(repository)

    escalation = create_escalation()

    repository.update.return_value = escalation

    result = service.assign(
        escalation=escalation,
        agent="agent_001",
    )

    assert result is escalation
    assert escalation.assigned_agent == "agent_001"
    assert escalation.status == "in_progress"

    repository.update.assert_called_once_with(escalation)


def test_resolve_moves_escalation_to_resolved():
    repository = Mock()
    service = HumanEscalationService(repository)

    escalation = create_escalation()
    escalation.status = "in_progress"

    repository.update.return_value = escalation

    result = service.resolve(
        escalation=escalation,
        agent_notes="Refund manually approved.",
    )

    assert result is escalation
    assert escalation.status == "resolved"
    assert escalation.agent_notes == "Refund manually approved."
    assert escalation.resolved_at is not None

    repository.update.assert_called_once_with(escalation)


def test_close_moves_resolved_escalation_to_closed():
    repository = Mock()
    service = HumanEscalationService(repository)

    escalation = create_escalation()
    escalation.status = "resolved"

    repository.update.return_value = escalation

    result = service.close(escalation)

    assert result is escalation
    assert escalation.status == "closed"

    repository.update.assert_called_once_with(escalation)


def test_cannot_assign_closed_escalation():
    repository = Mock()
    service = HumanEscalationService(repository)

    escalation = create_escalation()
    escalation.status = "closed"

    with pytest.raises(
        ValueError,
        match="Cannot assign a closed escalation.",
    ):
        service.assign(
            escalation=escalation,
            agent="agent_001",
        )

    repository.update.assert_not_called()


def test_cannot_resolve_closed_escalation():
    repository = Mock()
    service = HumanEscalationService(repository)

    escalation = create_escalation()
    escalation.status = "closed"

    with pytest.raises(
        ValueError,
        match="Escalation is already closed.",
    ):
        service.resolve(
            escalation=escalation,
            agent_notes="Done.",
        )

    repository.update.assert_not_called()


def test_cannot_close_open_escalation():
    repository = Mock()
    service = HumanEscalationService(repository)

    escalation = create_escalation()
    escalation.status = "open"

    with pytest.raises(
        ValueError,
        match="Only resolved escalations can be closed.",
    ):
        service.close(escalation)

    repository.update.assert_not_called()


def test_cannot_close_in_progress_escalation():
    repository = Mock()
    service = HumanEscalationService(repository)

    escalation = create_escalation()
    escalation.status = "in_progress"

    with pytest.raises(
        ValueError,
        match="Only resolved escalations can be closed.",
    ):
        service.close(escalation)

    repository.update.assert_not_called()