from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import SupportCase


class SupportCaseRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, support_case: SupportCase) -> SupportCase:
        self.db.add(support_case)
        self.db.commit()
        self.db.refresh(support_case)

        return support_case

    def get_by_id(self, case_id: int) -> SupportCase | None:
        stmt = select(SupportCase).where(
            SupportCase.id == case_id
        )

        return self.db.scalar(stmt)

    def get_by_customer_id(
        self,
        customer_id: int,
    ) -> list[SupportCase]:

        stmt = select(SupportCase).where(
            SupportCase.customer_id == customer_id
        )

        return list(self.db.scalars(stmt).all())

    def get_all(self) -> list[SupportCase]:
        stmt = select(SupportCase)

        return list(self.db.scalars(stmt).all())

    def update(self, support_case: SupportCase) -> SupportCase:
        self.db.commit()
        self.db.refresh(support_case)

        return support_case

    def delete(self, support_case: SupportCase) -> None:
        self.db.delete(support_case)
        self.db.commit()