from app.ai.gateway import LLMGateway
from app.ai.providers.xai import XAIProvider


def main():
    provider = XAIProvider()

    gateway = LLMGateway(provider)

    response = gateway.generate(
        "Explain what a duplicate payment means in one sentence."
    )

    print("\nGrok response:")
    print(response)


if __name__ == "__main__":
    main()