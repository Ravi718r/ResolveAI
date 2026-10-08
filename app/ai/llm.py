from app.ai.gateway import LLMGateway
from app.ai.model_router import ModelRouter
from app.ai.providers.groq import GroqProvider


def create_llm_gateway() -> LLMGateway:

    qwen = GroqProvider(
        model="qwen/qwen3.8-27b",
        temperature=0.0,
    )

    gpt_oss_120b = GroqProvider(
        model="openai/gpt-oss-120b",
        temperature=0.0,
    )

    gpt_oss_20b = GroqProvider(
        model="openai/gpt-oss-20b",
        temperature=0.0,
    )

    router = ModelRouter(
        qwen=qwen,
        gpt_oss_120b=gpt_oss_120b,
        gpt_oss_20b=gpt_oss_20b,
    )

    return LLMGateway(router)