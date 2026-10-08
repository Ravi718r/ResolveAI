from datetime import datetime, timezone

from app.db.models import SupportCase
from app.repositories.support_case import SupportCaseRepository


class SupportCaseService:

    def __init__(
        self,
        support_case_repository: SupportCaseRepository,
    ):
        self.support_case_repository = support_case_repository

    def get_case_by_id(
        self,
        case_id: int,
    ) -> SupportCase | None:

        return self.support_case_repository.get_by_id(case_id)

    def get_all_cases(
        self,
    ) -> list[SupportCase]:

        return self.support_case_repository.get_all()

    def get_cases_by_customer_id(
        self,
        customer_id: int,
    ) -> list[SupportCase]:

        return self.support_case_repository.get_by_customer_id(
            customer_id
        )

    def create_case(
        self,
        customer_id: int,
        order_id: int | None,
        issue_type: str,
        description: str,
    ) -> SupportCase:

        support_case = SupportCase(
            customer_id=customer_id,
            issue_type=issue_type,
            order_id=order_id,
            description=description,
            status="open",
            resolution=None,
            created_at=datetime.now(timezone.utc),
        )

        return self.support_case_repository.create(
            support_case
        )

    def update_status(
        self,
        case: SupportCase,
        status: str,
    ) -> SupportCase:

        case.status = status

        return self.support_case_repository.update(case)

    def resolve_case(
        self,
        case_id: int,
        resolution: str,
    ) -> SupportCase | None:

        support_case = self.support_case_repository.get_by_id(case_id)

        if support_case is None:
            return None

        support_case.status = "resolved"
        support_case.resolution = resolution

        return self.support_case_repository.update(support_case)