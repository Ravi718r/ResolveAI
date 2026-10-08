from datetime import datetime, timezone
from decimal import Decimal

from app.db.models import Order, Refund, SupportCase
from app.repositories.order import OrderRepository
from app.repositories.payment import PaymentRepository
from app.repositories.refund import RefundRepository
from app.repositories.support_case import SupportCaseRepository


# ============================================================
# Business status values currently supported by ResolveAI
# ============================================================

VALID_ORDER_STATUSES = {
    "pending",
    "successful",
    "completed",
    "failed",
    "cancelled",
}

ISSUE_TYPE_ALIASES = {
    # Payment failed
    "payment_failed": "payment_failed",
    "payment failure": "payment_failed",
    "failed payment": "payment_failed",
    "payment-failed": "payment_failed",

    # Refund
    "refund_request": "refund_request",
    "refund request": "refund_request",
    "refund": "refund_request",

    # Duplicate payment
    "duplicate_payment": "duplicate_payment",
    "duplicate payment": "duplicate_payment",
    "double payment": "duplicate_payment",

    # Missing order
    "missing_order": "missing_order",
    "missing order": "missing_order",
    "order missing": "missing_order",

    # Wrong order status
    "wrong_order_status": "wrong_order_status",
    "wrong order status": "wrong_order_status",
    "incorrect order status": "wrong_order_status",

    # Cancel order
    "cancel_order": "cancel_order",
    "cancel order": "cancel_order",
    "order cancellation": "cancel_order",
}

PAYMENT_SUCCESSFUL = "successful"
PAYMENT_FAILED = "failed"


class ResolutionService:

    def __init__(
        self,
        support_case_repository: SupportCaseRepository,
        order_repository: OrderRepository,
        payment_repository: PaymentRepository,
        refund_repository: RefundRepository,
    ):
        self.support_case_repository = support_case_repository
        self.order_repository = order_repository
        self.payment_repository = payment_repository
        self.refund_repository = refund_repository

    # ========================================================
    # Common helpers
    # ========================================================

    def _update_case(
        self,
        case: SupportCase,
        status: str,
        resolution: str,
    ) -> SupportCase:

        case.status = status
        case.resolution = resolution

        return self.support_case_repository.update(case)

    def _get_valid_order(
        self,
        case: SupportCase,
    ) -> tuple[Order | None, str | None]:

        if case.order_id is None:
            return None, (
                "No order is associated with this support case."
            )

        order = self.order_repository.get_by_id(
            case.order_id
        )

        if order is None:
            return None, (
                "Order associated with this support case "
                "could not be found."
            )

        if order.customer_id != case.customer_id:
            return None, (
                "The order does not belong to the customer "
                "associated with this support case."
            )

        return order, None

    def _case_is_already_resolved(
        self,
        case: SupportCase,
    ) -> bool:

        return case.status == "resolved"

    # ========================================================
    # 1. Payment Failed
    # ========================================================

    def resolve_payment_failed(
        self,
        case: SupportCase,
    ) -> SupportCase:

        if self._case_is_already_resolved(case):
            return case

        order, error = self._get_valid_order(case)

        if order is None:
            return self._update_case(
                case,
                "pending",
                error,
            )

        payment = self.payment_repository.get_by_order_id(
            order.id
        )

        if payment is None:
            return self._update_case(
                case,
                "pending",
                "No payment was found for the associated order.",
            )

        if payment.status == PAYMENT_FAILED:
            return self._update_case(
                case,
                "resolved",
                (
                    "Payment failure confirmed. "
                    "The customer can retry the payment."
                ),
            )

        return self._update_case(
            case,
            "pending",
            (
                f"Payment status is '{payment.status}'. "
                "Manual investigation is required."
            ),
        )

    # ========================================================
    # 2. Refund Request
    # ========================================================

    def resolve_refund_request(
        self,
        case: SupportCase,
    ) -> SupportCase:

        if self._case_is_already_resolved(case):
            return case

        order, error = self._get_valid_order(case)

        if order is None:
            return self._update_case(
                case,
                "pending",
                error,
            )

        payment = self.payment_repository.get_by_order_id(
            order.id
        )

        if payment is None:
            return self._update_case(
                case,
                "pending",
                "No payment was found for this order.",
            )

        if payment.status != PAYMENT_SUCCESSFUL:
            return self._update_case(
                case,
                "pending",
                (
                    "Refund cannot be processed because "
                    f"payment status is '{payment.status}'."
                ),
            )

        # Prevent duplicate refund creation.
        existing_refund = (
            self.refund_repository.get_by_payment_id(
                payment.id
            )
        )

        if existing_refund is not None:
            return self._update_case(
                case,
                "pending",
                (
                    "A refund already exists for this payment. "
                    "Manual investigation is required."
                ),
            )

        refund = Refund(
            payment_id=payment.id,
            amount=payment.amount,
            reason="Customer requested refund",
            status="pending",
            created_at=datetime.now(timezone.utc),
        )

        self.refund_repository.create(refund)

        return self._update_case(
            case,
            "resolved",
            (
                "Refund request created successfully for "
                f"{payment.amount} {order.currency}."
            ),
        )

    # ========================================================
    # 3. Duplicate Payment
    # ========================================================

    def resolve_duplicate_payment(
        self,
        case: SupportCase,
    ) -> SupportCase:

        if self._case_is_already_resolved(case):
            return case

        order, error = self._get_valid_order(case)

        if order is None:
            return self._update_case(
                case,
                "pending",
                error,
            )

        payments = (
            self.payment_repository.get_all_by_order_id(
                order.id
            )
        )

        # Only successful payments count as actual charges.
        successful_payments = [
            payment
            for payment in payments
            if payment.status == PAYMENT_SUCCESSFUL
        ]

        if len(successful_payments) < 2:
            return self._update_case(
                case,
                "pending",
                (
                    "No duplicate successful payment was found "
                    "for the associated order. "
                    "Manual investigation is required."
                ),
            )

        return self._update_case(
            case,
            "resolved",
            (
                "Duplicate successful payment detected. "
                f"{len(successful_payments)} successful payment "
                "records were found for the order."
            ),
        )

    # ========================================================
    # 4. Missing Order
    # ========================================================

    def resolve_missing_order(
        self,
        case: SupportCase,
    ) -> SupportCase:

        if self._case_is_already_resolved(case):
            return case

        if case.order_id is None:
            return self._update_case(
                case,
                "pending",
                (
                    "Unable to investigate the issue because "
                    "no order is associated with this support case."
                ),
            )

        order = self.order_repository.get_by_id(
            case.order_id
        )

        if order is None:
            return self._update_case(
                case,
                "pending",
                (
                    "Order associated with this support case "
                    "could not be found."
                ),
            )

        if order.customer_id != case.customer_id:
            return self._update_case(
                case,
                "pending",
                (
                    "The order does not belong to the customer "
                    "associated with this support case."
                ),
            )

        return self._update_case(
            case,
            "pending",
            (
                "Order was found. This case does not require "
                "missing-order resolution."
            ),
        )

    # ========================================================
    # 5. Wrong Order Status
    # ========================================================

    def resolve_wrong_order_status(
        self,
        case: SupportCase,
    ) -> SupportCase:

        if self._case_is_already_resolved(case):
            return case

        order, error = self._get_valid_order(case)

        if order is None:
            return self._update_case(
                case,
                "pending",
                error,
            )

        if order.status not in VALID_ORDER_STATUSES:
            return self._update_case(
                case,
                "pending",
                (
                    f"Invalid order status '{order.status}' "
                    "detected. Manual correction is required."
                ),
            )

        return self._update_case(
            case,
            "pending",
            (
                f"Order status '{order.status}' is valid. "
                "Manual investigation is required to determine "
                "why the customer sees an incorrect status."
            ),
        )

    # ========================================================
    # 6. Cancel Order
    # ========================================================

    def resolve_cancel_order(
        self,
        case: SupportCase,
    ) -> SupportCase:

        if self._case_is_already_resolved(case):
            return case

        order, error = self._get_valid_order(case)

        if order is None:
            return self._update_case(
                case,
                "pending",
                error,
            )

        # Pending orders can be cancelled automatically.
        if order.status == "pending":

            order.status = "cancelled"

            self.order_repository.update(order)

            return self._update_case(
                case,
                "resolved",
                (
                    f"Order {order.id} was successfully "
                    "cancelled."
                ),
            )

        # Already cancelled = requested final state already exists.
        if order.status == "cancelled":

            return self._update_case(
                case,
                "resolved",
                (
                    f"Order {order.id} was already cancelled."
                ),
            )

        # Successful/completed/failed orders are not
        # automatically cancelled.
        return self._update_case(
            case,
            "pending",
            (
                f"Order {order.id} cannot be automatically "
                f"cancelled because its current status is "
                f"'{order.status}'. Manual investigation is "
                "required."
            ),
        )

    
    # ========================================================
    # 7. Resolve Order
    # ========================================================
    
    def resolve(self, case: SupportCase) -> SupportCase:
        """
        Main entry point for resolving a support case.

        First normalizes the issue type and then sends
        the case to the correct deterministic business rule.
        """

        # Don't process an already resolved case again.
        if self._case_is_already_resolved(case):
            return case

        # Convert variations such as "failed payment"
        # into the canonical "payment_failed".
        issue_type = self._normalize_issue_type(case.issue_type)

        if issue_type == "payment_failed":
            return self.resolve_payment_failed(case)

        if issue_type == "refund_request":
            return self.resolve_refund_request(case)

        if issue_type == "duplicate_payment":
            return self.resolve_duplicate_payment(case)

        if issue_type == "missing_order":
            return self.resolve_missing_order(case)

        if issue_type == "wrong_order_status":
            return self.resolve_wrong_order_status(case)

        if issue_type == "cancel_order":
            return self.resolve_cancel_order(case)

        # Unknown issue types should not accidentally trigger
        # any business operation.
        case.status = "pending"
        case.resolution = (
            f"Unsupported issue type: {case.issue_type}. "
            "Manual investigation is required."
        )

        return self.support_case_repository.update(case)



    def _normalize_issue_type(self, issue_type: str) -> str | None:
        """
        Convert different user/input variations into
        one canonical issue type.
        """

        # Remove extra spaces and make comparison case-insensitive.
        normalized = issue_type.strip().lower()

        return ISSUE_TYPE_ALIASES.get(normalized)