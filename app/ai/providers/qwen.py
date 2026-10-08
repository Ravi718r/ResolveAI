import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from app.ai.providers.base import LLMProvider


load_dotenv()


class QwenProvider(LLMProvider):

    def __init__(
        self,
        model: str = "qwen/qwen3.8-27b",
        temperature: float = 0.0,
    ):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.llm = ChatGroq(
            model=model,
            temperature=temperature,
            api_key=api_key,
        )

    @property
    def name(self) -> str:
        return "qwen-groq"

    def generate(self, prompt: str) -> str:
        response = self.llm.invoke(prompt)
        return response.content