from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class LLMProvider(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        raise NotImplementedError

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a text response."""
        raise NotImplementedError

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        schema: type[T],
    ) -> T:
        """Generate a structured response matching a Pydantic schema."""
        raise NotImplementedError