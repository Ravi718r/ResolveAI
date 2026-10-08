from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.repositories.support_case import SupportCaseRepository
from app.repositories.order import OrderRepository
from app.repositories.payment import PaymentRepository
from app.repositories.refund import RefundRepository

from app.repositories.human_escalation import (
    HumanEscalationRepository,
)

from app.services.human_escalation_service import (
    HumanEscalationService,
)

from app.ai.response_generator import AIResponseGenerator

from app.services.resolution_service import ResolutionService

from app.ai.classifier import SupportClassifier
from app.ai.llm import create_llm_gateway
from app.ai.resolution_agent import AIResolutionService
from app.ai.response_generator import AIResponseGenerator

from app.schemas.ai_resolution import (
    AIResolutionRequest,
    AIResolutionResponse,
)


router = APIRouter(
    prefix="/ai",
    tags=["AI Resolution"],
)


def get_ai_resolution_service(
    db: Session = Depends(get_db),
) -> AIResolutionService:

    # Repositories
    support_case_repository = SupportCaseRepository(db)
    order_repository = OrderRepository(db)
    payment_repository = PaymentRepository(db)
    refund_repository = RefundRepository(db)
    escalation_repository = HumanEscalationRepository(db)

    escalation_service = HumanEscalationService(
        escalation_repository
    )

    # Deterministic business service
    resolution_service = ResolutionService(
        support_case_repository=support_case_repository,
        order_repository=order_repository,
        payment_repository=payment_repository,
        refund_repository=refund_repository,
    )

    # LLM
    gateway = create_llm_gateway()

    classifier = SupportClassifier(gateway)
    response_generator = AIResponseGenerator(gateway)

    # AI service
    return AIResolutionService(
        classifier=classifier,
        resolution_service=resolution_service,
        order_repository=order_repository,
        support_case_repository=support_case_repository,
        response_generator=response_generator,
        escalation_service=escalation_service,
    )


@router.post(
    "/resolve",
    response_model=AIResolutionResponse,
)
def resolve_with_ai(
    data: AIResolutionRequest,
    service: AIResolutionService = Depends(
        get_ai_resolution_service
    ),
):
    try:
        result, message, escalation = service.resolve(
            customer_id=data.customer_id,
            customer_message=data.customer_message,
        )

        return AIResolutionResponse(
            case_id=result.id,
            status=result.status,
            resolution=result.resolution,
            message=message,
            escalated=escalation is not None,
            escalation_id=(
                escalation.id
                if escalation is not None
                else None
            ),
            escalation_status=(
                escalation.status
                if escalation is not None
                else None
            ),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )