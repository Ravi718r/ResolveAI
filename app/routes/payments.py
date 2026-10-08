from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.payment import PaymentRepository
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services.payment_service import PaymentService


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


def get_payment_service(
    db: Session = Depends(get_db),
) -> PaymentService:
    repository = PaymentRepository(db)

    return PaymentService(repository)


@router.post(
    "/",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_payment(
    data: PaymentCreate,
    service: PaymentService = Depends(get_payment_service),
):
    try:
        return service.create_payment(
            order_id=data.order_id,
            transaction_id=data.transaction_id,
            amount=data.amount,
            status=data.status,
            payment_method=data.payment_method,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
)
def get_payment(
    payment_id: int,
    service: PaymentService = Depends(get_payment_service),
):
    payment = service.get_payment_by_id(payment_id)

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return payment


@router.get(
    "/transaction/{transaction_id}",
    response_model=PaymentResponse,
)
def get_payment_by_transaction(
    transaction_id: str,
    service: PaymentService = Depends(get_payment_service),
):
    payment = service.get_payment_by_transaction_id(
        transaction_id
    )

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return payment


@router.get(
    "/order/{order_id}",
    response_model=PaymentResponse,
)
def get_payment_by_order(
    order_id: int,
    service: PaymentService = Depends(get_payment_service),
):
    payment = service.get_payment_by_order_id(order_id)

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return payment