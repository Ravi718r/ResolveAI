from datetime import UTC, datetime

from app.db.models import HumanEscalation, SupportCase


def create_escalation(db_session):
    case = SupportCase(
        customer_id=1,
        order_id=None,
        issue_type="missing_order",
        description="My order is missing.",
        status="pending",
        resolution="Manual investigation required.",
        created_at=datetime.now(UTC),
    )

    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

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


def test_get_escalations(client, db_session):

    escalation = create_escalation(db_session)

    response = client.get("/escalations")

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 1

    found = next(
        item
        for item in data
        if item["id"] == escalation.id
    )

    assert found["status"] == "open"
    assert found["support_case_id"] == escalation.support_case_id


def test_get_escalation_by_id(client, db_session):

    escalation = create_escalation(db_session)

    response = client.get(
        f"/escalations/{escalation.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == escalation.id
    assert data["status"] == "open"
    assert data["reason"] == (
        "Manual investigation required."
    )


def test_get_nonexistent_escalation(client):

    response = client.get("/escalations/99999")

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Escalation not found."
    )


def test_assign_escalation(client, db_session):

    escalation = create_escalation(db_session)

    response = client.patch(
        f"/escalations/{escalation.id}/assign",
        json={
            "agent": "agent_001",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == escalation.id
    assert data["status"] == "in_progress"
    assert data["assigned_agent"] == "agent_001"


def test_resolve_escalation(client, db_session):

    escalation = create_escalation(db_session)

    client.patch(
        f"/escalations/{escalation.id}/assign",
        json={
            "agent": "agent_001",
        },
    )

    response = client.patch(
        f"/escalations/{escalation.id}/resolve",
        json={
            "agent_notes": "Issue resolved manually.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == escalation.id
    assert data["status"] == "resolved"
    assert data["assigned_agent"] == "agent_001"
    assert data["agent_notes"] == (
        "Issue resolved manually."
    )
    assert data["resolved_at"] is not None


def test_close_escalation(client, db_session):

    escalation = create_escalation(db_session)

    client.patch(
        f"/escalations/{escalation.id}/assign",
        json={
            "agent": "agent_001",
        },
    )

    client.patch(
        f"/escalations/{escalation.id}/resolve",
        json={
            "agent_notes": "Issue resolved manually.",
        },
    )

    response = client.patch(
        f"/escalations/{escalation.id}/close"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == escalation.id
    assert data["status"] == "closed"


def test_cannot_close_open_escalation(
    client,
    db_session,
):

    escalation = create_escalation(db_session)

    response = client.patch(
        f"/escalations/{escalation.id}/close"
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Only resolved escalations can be closed."
    )


def test_cannot_assign_closed_escalation(
    client,
    db_session,
):

    escalation = create_escalation(db_session)

    client.patch(
        f"/escalations/{escalation.id}/assign",
        json={"agent": "agent_001"},
    )

    client.patch(
        f"/escalations/{escalation.id}/resolve",
        json={
            "agent_notes": "Resolved.",
        },
    )

    client.patch(
        f"/escalations/{escalation.id}/close"
    )

    response = client.patch(
        f"/escalations/{escalation.id}/assign",
        json={"agent": "agent_002"},
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Cannot assign a closed escalation."
    )


def test_cannot_resolve_closed_escalation(
    client,
    db_session,
):

    escalation = create_escalation(db_session)

    client.patch(
        f"/escalations/{escalation.id}/assign",
        json={"agent": "agent_001"},
    )

    client.patch(
        f"/escalations/{escalation.id}/resolve",
        json={
            "agent_notes": "Resolved.",
        },
    )

    client.patch(
        f"/escalations/{escalation.id}/close"
    )

    response = client.patch(
        f"/escalations/{escalation.id}/resolve",
        json={
            "agent_notes": "Trying again.",
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Escalation is already closed."
    )