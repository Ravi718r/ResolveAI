import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from app.ai.providers.base import LLMProvider


load_dotenv()


class GeminiProvider(LLMProvider):

    def __init__(
        self,
        model: str = "gemini-3.8-flash",
        temperature: float = 0.0,
    ):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            google_api_key=api_key,
        )

    def generate(self, prompt: str) -> str:
        response = self.llm.invoke(prompt)

        return response.content

    
    @property
    def name(self) -> str:
        return "gemini"