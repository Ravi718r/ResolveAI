from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.support_case import SupportCaseRepository
from app.repositories.order import OrderRepository
from app.repositories.payment import PaymentRepository
from app.repositories.refund import RefundRepository

from app.schemas.resolution import (
    ResolutionRequest,
    ResolutionResponse,
)

from app.services.resolution_service import ResolutionService


router = APIRouter(
    prefix="/resolution",
    tags=["Resolution"],
)


def get_resolution_service(
    db: Session = Depends(get_db),
) -> ResolutionService:
    """
    Build ResolutionService with all required repositories.
    """

    support_case_repository = SupportCaseRepository(db)
    order_repository = OrderRepository(db)
    payment_repository = PaymentRepository(db)
    refund_repository = RefundRepository(db)

    return ResolutionService(
        support_case_repository=support_case_repository,
        order_repository=order_repository,
        payment_repository=payment_repository,
        refund_repository=refund_repository,
    )


@router.post(
    "/resolve",
    response_model=ResolutionResponse,
)
@router.post(
    "/resolve",
    response_model=ResolutionResponse,
)
def resolve_support_case(
    data: ResolutionRequest,
    service: ResolutionService = Depends(get_resolution_service),
):
    """
    Resolve a support case using deterministic business rules.
    """

    # Get the support case first.
    case = service.support_case_repository.get_by_id(data.case_id)

    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Support case not found",
        )

    # Let ResolutionService handle:
    # - issue type normalization
    # - issue type routing
    # - business rules
    # - unsupported issue types
    result = service.resolve(case)

    return ResolutionResponse(
        case_id=result.id,
        status=result.status,
        resolution=result.resolution,
    )