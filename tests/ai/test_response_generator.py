from unittest.mock import Mock

from app.ai.response_generator import AIResponseGenerator
from app.ai.tasks import LLMTask


def test_response_generator_returns_llm_response():

    gateway = Mock()

    gateway_response = Mock()
    gateway_response.content = (
        "Your duplicate payment issue has been resolved."
    )

    gateway.generate.return_value = gateway_response

    generator = AIResponseGenerator(gateway)

    result = generator.generate(
        customer_message="I was charged twice for order 100.",
        issue_type="duplicate_payment",
        status="resolved",
        resolution="Duplicate payment detected and refund initiated.",
    )

    assert result == (
        "Your duplicate payment issue has been resolved."
    )

    gateway.generate.assert_called_once()


def test_response_generator_uses_simple_task():

    gateway = Mock()

    gateway_response = Mock()
    gateway_response.content = "Your issue has been resolved."

    gateway.generate.return_value = gateway_response

    generator = AIResponseGenerator(gateway)

    generator.generate(
        customer_message="My payment failed.",
        issue_type="payment_failed",
        status="resolved",
        resolution="Payment failure resolved.",
    )

    call_args = gateway.generate.call_args

    assert call_args.kwargs["task"] == LLMTask.SIMPLE


def test_response_generator_includes_resolution_context():

    gateway = Mock()

    gateway_response = Mock()
    gateway_response.content = "Your issue has been resolved."

    gateway.generate.return_value = gateway_response

    generator = AIResponseGenerator(gateway)

    generator.generate(
        customer_message="I was charged twice.",
        issue_type="duplicate_payment",
        status="resolved",
        resolution="Duplicate payment detected.",
    )

    prompt = gateway.generate.call_args.kwargs["prompt"]

    assert "I was charged twice." in prompt
    assert "duplicate_payment" in prompt
    assert "resolved" in prompt
    assert "Duplicate payment detected." in prompt


def test_response_generator_propagates_gateway_error():

    gateway = Mock()

    gateway.generate.side_effect = RuntimeError(
        "LLM provider unavailable"
    )

    generator = AIResponseGenerator(gateway)

    try:
        generator.generate(
            customer_message="My payment failed.",
            issue_type="payment_failed",
            status="resolved",
            resolution="Payment failure resolved.",
        )
        assert False, "Expected RuntimeError"
    except RuntimeError as exc:
        assert "LLM provider unavailable" in str(exc)


def test_response_generator_tells_customer_when_case_is_pending():

    gateway = Mock()

    gateway_response = Mock()
    gateway_response.content = (
        "Your issue requires further investigation."
    )

    gateway.generate.return_value = gateway_response

    generator = AIResponseGenerator(gateway)

    result = generator.generate(
        customer_message="I cannot find my order.",
        issue_type="missing_order",
        status="pending",
        resolution=None,
    )

    assert result == (
        "Your issue requires further investigation."
    )

    prompt = gateway.generate.call_args.kwargs["prompt"]

    assert "PENDING" in prompt
    assert "MUST NOT say that the issue was resolved" in prompt


def test_response_generator_tells_customer_when_case_is_resolved():

    gateway = Mock()

    gateway_response = Mock()
    gateway_response.content = (
        "Your duplicate payment issue has been resolved."
    )

    gateway.generate.return_value = gateway_response

    generator = AIResponseGenerator(gateway)

    result = generator.generate(
        customer_message="I was charged twice.",
        issue_type="duplicate_payment",
        status="resolved",
        resolution="Duplicate payment detected.",
    )

    assert result == (
        "Your duplicate payment issue has been resolved."
    )

    prompt = gateway.generate.call_args.kwargs["prompt"]

    assert "RESOLVED" in prompt
    assert "successfully resolved" in prompt