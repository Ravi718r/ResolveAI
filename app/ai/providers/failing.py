from app.ai.providers.base import LLMProvider


class FailingProvider(LLMProvider):

    @property
    def name(self) -> str:
        return "fake-failing-model"

    def generate(self, prompt: str) -> str:
        raise RuntimeError("Simulated model failure")