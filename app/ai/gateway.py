from dataclasses import dataclass
from typing import TypeVar

from pydantic import BaseModel
from app.ai.model_router import ModelRouter
from app.ai.tasks import LLMTask



T = TypeVar("T", bound=BaseModel)

@dataclass
class LLMResponse:
    content: str
    provider: str
    attempts: int
    fallback_used: bool


class LLMGateway:

    def __init__(self, router: ModelRouter):
        self.router = router

    def generate(
        self,
        prompt: str,
        task: LLMTask = LLMTask.GENERAL,
    ) -> LLMResponse:

        providers = self.router.fallback_chain(task)

        last_error = None

        for attempt, provider in enumerate(providers, start=1):

            try:
                content = provider.generate(prompt)

                return LLMResponse(
                    content=content,
                    provider=provider.name,
                    attempts=attempt,
                    fallback_used=attempt > 1,
                )

            except Exception as error:
                last_error = error

                print(
                    f"[LLM Gateway] "
                    f"{provider.name} failed on attempt {attempt}: {error}"
                )

        raise RuntimeError(
            f"All LLM providers failed for task '{task}'."
        ) from last_error


    def generate_structured(
        self,
        prompt: str,
        schema: type[T],
        task: LLMTask = LLMTask.GENERAL,
    ) -> tuple[T, str, int, bool]:

        providers = self.router.fallback_chain(task)

        last_error = None

        for attempt, provider in enumerate(providers, start=1):

            try:
                result = provider.generate_structured(
                    prompt=prompt,
                    schema=schema,
                )

                return (
                    result,
                    provider.name,
                    attempt,
                    attempt > 1,
                )

            except Exception as error:
                last_error = error

                print(
                    f"[LLM Gateway] "
                    f"{provider.name} failed on structured attempt "
                    f"{attempt}: {error}"
                )

        raise RuntimeError(
            f"All LLM providers failed for task '{task}'."
        ) from last_error