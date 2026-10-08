import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from app.ai.providers.base import LLMProvider


load_dotenv()


class XAIProvider(LLMProvider):

    def __init__(
        self,
        model: str = "grok-4.7",
        temperature: float = 0.0,
    ):
        api_key = os.getenv("XAI_API_KEY")

        if not api_key:
            raise ValueError(
                "XAI_API_KEY is not configured."
            )

        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key,
            base_url="https://api.x.ai/v1",
        )

    def generate(self, prompt: str) -> str:
        response = self.llm.invoke(prompt)
        return response.content

    @property
    def name(self) -> str:
        return "xai"