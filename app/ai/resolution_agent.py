from app.ai.classifier import SupportClassifier
from app.ai.schemas import CustomerIssue
from app.db.models import HumanEscalation, SupportCase
from app.services.human_escalation_service import (
    HumanEscalationService,
)
from app.services.resolution_service import ResolutionService


class AIResolutionService:

    def __init__(
        self,
        classifier: SupportClassifier,
        resolution_service: ResolutionService,
        order_repository,
        support_case_repository,
        response_generator,
        escalation_service: HumanEscalationService,
    ):
        self.classifier = classifier
        self.resolution_service = resolution_service
        self.order_repository = order_repository
        self.support_case_repository = support_case_repository
        self.response_generator = response_generator
        self.escalation_service = escalation_service

    def resolve(
        self,
        customer_id: int,
        customer_message: str,
    ) -> tuple[SupportCase, str, HumanEscalation | None]:

        # 1. Classify customer message
        issue: CustomerIssue = self.classifier.classify(
            customer_message
        )

        # 2. Reject low-confidence classifications
        if issue.confidence < 0.80:
            raise ValueError(
                "Classification confidence is too low "
                "for automatic resolution."
            )

        # 3. Validate order ownership
        if issue.order_id is not None:

            order = self.order_repository.get_by_id(
                issue.order_id
            )

            if order is None:
                raise ValueError(
                    "The order mentioned by the customer "
                    "could not be found."
                )

            if order.customer_id != customer_id:
                raise ValueError(
                    "The order does not belong to this customer."
                )

        # 4. Create support case
        case = SupportCase(
            customer_id=customer_id,
            order_id=issue.order_id,
            issue_type=issue.issue_type,
            description=customer_message,
            status="open",
            resolution=None,
        )

        case = self.support_case_repository.create(case)

        # 5. Resolve using deterministic business logic
        case = self.resolution_service.resolve(case)

        # 6. Escalate unresolved cases
        escalation = None

        if case.status == "pending":
            escalation = self.escalation_service.escalate(
                case=case,
                reason=(
                    case.resolution
                    or "Automatic resolution was not possible."
                ),
            )

        # 7. Generate customer-facing response
        message = self.response_generator.generate(
            customer_message=customer_message,
            issue_type=issue.issue_type,
            status=case.status,
            resolution=case.resolution,
        )

        # 8. Return case, customer response, and escalation
        return case, message, escalation