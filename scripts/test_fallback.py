from app.ai.gateway import LLMGateway
from app.ai.model_router import ModelRouter
from app.ai.providers.failing import FailingProvider
from app.ai.providers.groq import GroqProvider
from app.ai.tasks import LLMTask


def main():

    failing_provider = FailingProvider()

    qwen = GroqProvider(
        model="qwen/qwen3.8-27b",
        temperature=0.0,
    )

    gpt_oss_120b = GroqProvider(
        model="openai/gpt-oss-120b",
        temperature=0.0,
    )

    router = ModelRouter(
        qwen=qwen,
        gpt_oss_120b=gpt_oss_120b,
        gpt_oss_20b=failing_provider,
    )

    gateway = LLMGateway(router)

    response = gateway.generate(
        "What is 2 + 2?",
        task=LLMTask.SIMPLE,
    )

    print("\n--- FALLBACK TEST ---")
    print("Response:", response.content)
    print("Provider:", response.provider)
    print("Attempts:", response.attempts)
    print("Fallback used:", response.fallback_used)


if __name__ == "__main__":
    main()