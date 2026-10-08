from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.customer import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerResponse
from app.services.customer_service import CustomerService


router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


def get_customer_service(
    db: Session = Depends(get_db),
) -> CustomerService:
    repository = CustomerRepository(db)

    return CustomerService(repository)


@router.post(
    "/",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    data: CustomerCreate,
    service: CustomerService = Depends(get_customer_service),
):
    try:
        return service.create_customer(
            name=data.name,
            email=data.email,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.get(
    "/",
    response_model=list[CustomerResponse],
    status_code=status.HTTP_200_OK,
)
def get_customers(
    service: CustomerService = Depends(
        get_customer_service
    ),
):
    return service.list_customers()


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
)
def get_customer(
    customer_id: int,
    service: CustomerService = Depends(get_customer_service),
):
    customer = service.get_customer(customer_id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    return customer