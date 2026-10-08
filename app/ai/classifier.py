from app.ai.gateway import LLMGateway
from app.ai.schemas import CustomerIssue
from app.ai.tasks import LLMTask


class SupportClassifier:

    def __init__(self, gateway: LLMGateway):
        self.gateway = gateway

    def classify(
        self,
        customer_message: str,
    ) -> CustomerIssue:

        prompt = f"""
You are a customer support issue classifier.

Classify the customer's message into exactly one of these issue types:

- payment_failed
- refund_request
- duplicate_payment
- missing_order
- wrong_order_status
- cancel_order

Extract the order_id if the customer mentions one.

Return your confidence as a number between 0 and 1.

Customer message:
{customer_message}
"""

        result, provider, attempts, fallback_used = (
            self.gateway.generate_structured(
                prompt=prompt,
                schema=CustomerIssue,
                task=LLMTask.AGENT,
            )
        )

        return result