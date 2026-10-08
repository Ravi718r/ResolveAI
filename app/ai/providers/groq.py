import os
from typing import TypeVar

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel

from app.ai.providers.base import LLMProvider


load_dotenv()

T = TypeVar("T", bound=BaseModel)


class GroqProvider(LLMProvider):

    def __init__(
        self,
        model: str,
        temperature: float = 0.0,
    ):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.model = model

        self.llm = ChatGroq(
            model=model,
            temperature=temperature,
            api_key=api_key,
        )

    @property
    def name(self) -> str:
        return f"groq:{self.model}"

    def generate(self, prompt: str) -> str:
        response = self.llm.invoke(prompt)
        return response.content

    def generate_structured(
        self,
        prompt: str,
        schema: type[T],
    ) -> T:

        structured_llm = self.llm.with_structured_output(schema)

        response = structured_llm.invoke(prompt)

        return response