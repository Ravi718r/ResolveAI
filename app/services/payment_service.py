from datetime import datetime, timezone
from decimal import Decimal

from app.db.models import Payment, SupportCase
from app.repositories.payment import PaymentRepository


class PaymentService:

    def __init__(self, payment_repository: PaymentRepository):
        self.payment_repository = payment_repository

    def get_payment_by_id(
        self,
        payment_id: int,
    ) -> Payment | None:
        return self.payment_repository.get_by_id(payment_id)

    def get_payment_by_transaction_id(
        self,
        transaction_id: str,
    ) -> Payment | None:
        return self.payment_repository.get_by_transaction_id(
            transaction_id
        )

    def get_payment_by_order_id(
        self,
        order_id: int,
    ) -> Payment | None:
        return self.payment_repository.get_by_order_id(order_id)

    def create_payment(
        self,
        order_id: int,
        transaction_id: str,
        amount: Decimal,
        status: str,
        payment_method: str,
    ) -> Payment:

        payment = Payment(
            order_id=order_id,
            transaction_id=transaction_id,
            amount=amount,
            status=status,
            payment_method=payment_method,
            created_at=datetime.now(timezone.utc),
        )

        return self.payment_repository.create(payment)

    
    
    def resolve_duplicate_payment(self, case: SupportCase) -> SupportCase:
        if case.order_id is None:
            case.status = "pending"
            case.resolution = (
                "Unable to investigate duplicate payment because "
                "no order is associated with this support case."
            )
            return self.support_case_repository.update(case)

        order = self.order_repository.get_by_id(case.order_id)

        if order is None:
            case.status = "pending"
            case.resolution = (
                "Order associated with this support case "
                "could not be found."
            )
            return self.support_case_repository.update(case)

        payments = self.payment_repository.get_all_by_order_id(order.id)

        if len(payments) < 2:
            case.status = "pending"
            case.resolution = (
                "No duplicate payment was found for the associated order. "
                "Manual investigation is required."
            )
            return self.support_case_repository.update(case)

        case.status = "resolved"
        case.resolution = (
            f"Duplicate payment detected. "
            f"{len(payments)} payment records were found for the order."
        )

        return self.support_case_repository.update(case)


    def resolve_missing_order(self, case: SupportCase) -> SupportCase:
        if case.order_id is None:
            case.status = "pending"
            case.resolution = (
                "Unable to investigate the issue because "
                "no order is associated with this support case."
            )
            return self.support_case_repository.update(case)

        order = self.order_repository.get_by_id(case.order_id)

        if order is None:
            case.status = "pending"
            case.resolution = (
                "Order associated with this support case "
                "could not be found."
            )
            return self.support_case_repository.update(case)

        case.status = "pending"
        case.resolution = (
            "Order was found. This case does not require "
            "missing-order resolution."
        )

        return self.support_case_repository.update(case)