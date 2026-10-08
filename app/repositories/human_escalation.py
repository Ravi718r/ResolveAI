from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import HumanEscalation


class HumanEscalationRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        escalation: HumanEscalation,
    ) -> HumanEscalation:

        self.db.add(escalation)
        self.db.commit()
        self.db.refresh(escalation)

        return escalation

    def get_by_id(
        self,
        escalation_id: int,
    ) -> HumanEscalation | None:

        return self.db.get(
            HumanEscalation,
            escalation_id,
        )

    def get_by_case_id(
        self,
        support_case_id: int,
    ) -> HumanEscalation | None:

        stmt = select(HumanEscalation).where(
            HumanEscalation.support_case_id
            == support_case_id
        )

        return self.db.scalars(stmt).first()

    def get_all(self) -> list[HumanEscalation]:

        stmt = select(HumanEscalation).order_by(
            HumanEscalation.created_at.desc()
        )

        return list(self.db.scalars(stmt).all())

    def update(
        self,
        escalation: HumanEscalation,
    ) -> HumanEscalation:

        escalation.updated_at = datetime.now(UTC)

        self.db.commit()
        self.db.refresh(escalation)

        return escalation