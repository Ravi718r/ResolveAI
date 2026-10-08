from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.refund import RefundRepository
from app.schemas.refund import RefundCreate, RefundResponse
from app.services.refund_service import RefundService


router = APIRouter(
    prefix="/refunds",
    tags=["Refunds"],
)


def get_refund_service(
    db: Session = Depends(get_db),
) -> RefundService:

    repository = RefundRepository(db)

    return RefundService(repository)


@router.post(
    "/",
    response_model=RefundResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_refund(
    data: RefundCreate,
    service: RefundService = Depends(get_refund_service),
) -> RefundResponse:

    return service.create_refund(
        payment_id=data.payment_id,
        amount=data.amount,
        reason=data.reason,
    )


@router.get(
    "/{refund_id}",
    response_model=RefundResponse,
)
def get_refund(
    refund_id: int,
    service: RefundService = Depends(get_refund_service),
) -> RefundResponse:

    refund = service.get_refund_by_id(refund_id)

    if refund is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refund not found",
        )

    return refund


@router.get(
    "/payment/{payment_id}",
    response_model=RefundResponse,
)
def get_refund_by_payment(
    payment_id: int,
    service: RefundService = Depends(get_refund_service),
) -> RefundResponse:

    refund = service.get_refund_by_payment_id(payment_id)

    if refund is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refund not found for this payment",
        )

    return refund