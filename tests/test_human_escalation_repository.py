from datetime import UTC, datetime

from app.db.models import HumanEscalation, SupportCase
from app.repositories.human_escalation import (
    HumanEscalationRepository,
)


def create_case(db_session):
    case = SupportCase(
        customer_id=1,
        order_id=100,
        issue_type="missing_order",
        description="My order is missing.",
        status="pending",
        resolution="Manual investigation required.",
        created_at=datetime.now(UTC),
    )

    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    return case


def create_escalation(db_session, case):
    escalation = HumanEscalation(
        support_case_id=case.id,
        status="open",
        reason="Manual investigation required.",
        assigned_agent=None,
        agent_notes=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        resolved_at=None,
    )

    db_session.add(escalation)
    db_session.commit()
    db_session.refresh(escalation)

    return escalation


def test_create_and_get_escalation(db_session):

    repository = HumanEscalationRepository(db_session)

    case = create_case(db_session)

    escalation = HumanEscalation(
        support_case_id=case.id,
        status="open",
        reason="Manual investigation required.",
        assigned_agent=None,
        agent_notes=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        resolved_at=None,
    )

    created = repository.create(escalation)

    assert created.id is not None
    assert created.support_case_id == case.id
    assert created.status == "open"

    result = repository.get_by_id(created.id)

    assert result is not None
    assert result.id == created.id


def test_get_by_case_id(db_session):

    repository = HumanEscalationRepository(db_session)

    case = create_case(db_session)
    escalation = create_escalation(db_session, case)

    result = repository.get_by_case_id(case.id)

    assert result is not None
    assert result.id == escalation.id
    assert result.support_case_id == case.id


def test_get_by_case_id_returns_none_when_not_found(
    db_session,
):

    repository = HumanEscalationRepository(db_session)

    result = repository.get_by_case_id(99999)

    assert result is None


def test_get_all_returns_escalations(db_session):

    repository = HumanEscalationRepository(db_session)

    case = create_case(db_session)
    create_escalation(db_session, case)

    result = repository.get_all()

    assert len(result) >= 1
    assert all(
        isinstance(item, HumanEscalation)
        for item in result
    )


def test_update_escalation(db_session):

    repository = HumanEscalationRepository(db_session)

    case = create_case(db_session)
    escalation = create_escalation(db_session, case)

    escalation.assigned_agent = "agent_001"
    escalation.status = "in_progress"

    updated = repository.update(escalation)

    assert updated.assigned_agent == "agent_001"
    assert updated.status == "in_progress"