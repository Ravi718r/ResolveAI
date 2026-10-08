from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.order import OrderRepository
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import OrderService


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


def get_order_service(
    db: Session = Depends(get_db),
) -> OrderService:

    repository = OrderRepository(db)

    return OrderService(repository)


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    data: OrderCreate,
    service: OrderService = Depends(get_order_service),
):
    return service.create_order(
        customer_id=data.customer_id,
        amount=data.amount,
        currency=data.currency,
        status=data.status,
    )


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
def get_order(
    order_id: int,
    service: OrderService = Depends(get_order_service),
):
    order = service.get_order_by_id(order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return order


@router.get(
    "/customer/{customer_id}",
    response_model=list[OrderResponse],
)
def get_customer_orders(
    customer_id: int,
    service: OrderService = Depends(get_order_service),
):
    return service.get_orders_by_customer_id(customer_id)


@router.get(
    "/",
    response_model=list[OrderResponse],
)
def get_orders(
    service: OrderService = Depends(
        get_order_service
    ),
):
    return service.list_orders()
