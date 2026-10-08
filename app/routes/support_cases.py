from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.support_case import SupportCaseRepository
from app.schemas.support_case import (
    SupportCaseCreate,
    SupportCaseResolve,
    SupportCaseResponse,
)
from app.services.support_case_service import SupportCaseService


router = APIRouter(
    prefix="/support-cases",
    tags=["Support Cases"],
)


def get_support_case_service(
    db: Session = Depends(get_db),
) -> SupportCaseService:
    repository = SupportCaseRepository(db)
    return SupportCaseService(repository)


@router.post(
    "/",
    response_model=SupportCaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_support_case(
    data: SupportCaseCreate,
    service: SupportCaseService = Depends(get_support_case_service),
):
    return service.create_case(
        customer_id=data.customer_id,
        order_id=data.order_id,
        issue_type=data.issue_type,
        description=data.description,
    )


@router.get(
    "/",
    response_model=list[SupportCaseResponse],
)
def get_all_support_cases(
    service: SupportCaseService = Depends(get_support_case_service),
):
    return service.get_all_cases()


@router.get(
    "/customer/{customer_id}",
    response_model=list[SupportCaseResponse],
)
def get_customer_support_cases(
    customer_id: int,
    service: SupportCaseService = Depends(get_support_case_service),
):
    return service.get_cases_by_customer_id(customer_id)


@router.get(
    "/{case_id}",
    response_model=SupportCaseResponse,
)
def get_support_case(
    case_id: int,
    service: SupportCaseService = Depends(get_support_case_service),
):
    support_case = service.get_case_by_id(case_id)

    if support_case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Support case not found",
        )

    return support_case


@router.patch(
    "/{case_id}/resolve",
    response_model=SupportCaseResponse,
)
def resolve_support_case(
    case_id: int,
    data: SupportCaseResolve,
    service: SupportCaseService = Depends(get_support_case_service),
):
    support_case = service.resolve_case(
        case_id=case_id,
        resolution=data.resolution,
    )

    if support_case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Support case not found",
        )

    return support_case


@router.delete(
    "/{case_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_support_case(
    case_id: int,
    service: SupportCaseService = Depends(get_support_case_service),
):
    deleted = service.delete_case(case_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Support case not found",
        )