from datetime import UTC, datetime

from app.db.models import HumanEscalation, SupportCase
from app.repositories.human_escalation import (
    HumanEscalationRepository,
)


class HumanEscalationService:

    def __init__(
        self,
        escalation_repository: HumanEscalationRepository,
    ):
        self.escalation_repository = escalation_repository

    def escalate(
        self,
        case: SupportCase,
        reason: str,
    ) -> HumanEscalation:

        existing = self.escalation_repository.get_by_case_id(
            case.id
        )

        if existing is not None:
            return existing

        escalation = HumanEscalation(
            support_case_id=case.id,
            status="open",
            reason=reason,
            assigned_agent=None,
            agent_notes=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            resolved_at=None,
        )

        return self.escalation_repository.create(
            escalation
        )

    def assign(
        self,
        escalation: HumanEscalation,
        agent: str,
    ) -> HumanEscalation:

        if escalation.status in {"resolved", "closed"}:
            raise ValueError(
                "Cannot assign a closed escalation."
            )

        escalation.assigned_agent = agent
        escalation.status = "in_progress"

        return self.escalation_repository.update(
            escalation
        )

    def resolve(
        self,
        escalation: HumanEscalation,
        agent_notes: str,
    ) -> HumanEscalation:

        if escalation.status == "closed":
            raise ValueError(
                "Escalation is already closed."
            )

        escalation.status = "resolved"
        escalation.agent_notes = agent_notes
        escalation.resolved_at = datetime.now(UTC)

        return self.escalation_repository.update(
            escalation
        )

    def close(
        self,
        escalation: HumanEscalation,
    ) -> HumanEscalation:

        if escalation.status != "resolved":
            raise ValueError(
                "Only resolved escalations can be closed."
            )

        escalation.status = "closed"

        return self.escalation_repository.update(
            escalation
        )