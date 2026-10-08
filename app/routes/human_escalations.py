from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.human_escalation import (
    HumanEscalationRepository,
)
from app.services.human_escalation_service import (
    HumanEscalationService,
)
from app.schemas.human_escalation import (
    AssignEscalationRequest,
    EscalationResponse,
    ResolveEscalationRequest,
)


router = APIRouter(
    prefix="/escalations",
    tags=["Human Escalations"],
)


def get_escalation_service(
    db: Session = Depends(get_db),
) -> HumanEscalationService:

    repository = HumanEscalationRepository(db)

    return HumanEscalationService(repository)


@router.get(
    "",
    response_model=list[EscalationResponse],
)
def get_escalations(
    db: Session = Depends(get_db),
):

    repository = HumanEscalationRepository(db)

    return repository.get_all()


@router.get(
    "/{escalation_id}",
    response_model=EscalationResponse,
)
def get_escalation(
    escalation_id: int,
    db: Session = Depends(get_db),
):

    repository = HumanEscalationRepository(db)

    escalation = repository.get_by_id(
        escalation_id
    )

    if escalation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation not found.",
        )

    return escalation


@router.patch(
    "/{escalation_id}/assign",
    response_model=EscalationResponse,
)
def assign_escalation(
    escalation_id: int,
    data: AssignEscalationRequest,
    service: HumanEscalationService = Depends(
        get_escalation_service
    ),
):

    escalation = service.escalation_repository.get_by_id(
        escalation_id
    )

    if escalation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation not found.",
        )

    try:
        return service.assign(
            escalation=escalation,
            agent=data.agent,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.patch(
    "/{escalation_id}/resolve",
    response_model=EscalationResponse,
)
def resolve_escalation(
    escalation_id: int,
    data: ResolveEscalationRequest,
    service: HumanEscalationService = Depends(
        get_escalation_service
    ),
):

    escalation = service.escalation_repository.get_by_id(
        escalation_id
    )

    if escalation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation not found.",
        )

    try:
        return service.resolve(
            escalation=escalation,
            agent_notes=data.agent_notes,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.patch(
    "/{escalation_id}/close",
    response_model=EscalationResponse,
)
def close_escalation(
    escalation_id: int,
    service: HumanEscalationService = Depends(
        get_escalation_service
    ),
):

    escalation = service.escalation_repository.get_by_id(
        escalation_id
    )

    if escalation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation not found.",
        )

    try:
        return service.close(
            escalation=escalation,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )