from app.ai.gateway import LLMGateway
from app.ai.model_router import ModelRouter
from app.ai.providers.base import LLMProvider
from app.ai.tasks import LLMTask


class FakeProvider(LLMProvider):

    @property
    def name(self) -> str:
        return "fake"

    def generate(self, prompt: str) -> str:
        return "fake response"

    def generate_structured(self, prompt: str, schema):
        raise NotImplementedError


def test_llm_gateway():

    provider = FakeProvider()

    router = ModelRouter(
        qwen=provider,
        gpt_oss_120b=provider,
        gpt_oss_20b=provider,
    )

    gateway = LLMGateway(router)

    response = gateway.generate("Hello ResolveAI")

    assert response.content == "fake response"
    assert response.provider == "fake"
    assert response.attempts == 1
    assert response.fallback_used is False