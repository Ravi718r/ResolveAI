from app.ai.gateway import LLMGateway
from app.ai.providers.groq import GroqProvider


def main():
    provider = GroqProvider()

    gateway = LLMGateway(provider)

    response = gateway.generate(
        "Explain what a duplicate payment means in one sentence."
    )

    print("\nGroq response:")
    print(response)


if __name__ == "__main__":
    main()