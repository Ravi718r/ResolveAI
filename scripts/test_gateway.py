from app.ai.llm import create_llm_gateway
from app.ai.tasks import LLMTask


def main():

    gateway = create_llm_gateway()

    simple_response = gateway.generate(
        "What is 2 + 2?",
        task=LLMTask.SIMPLE,
    )

    print("\n--- SIMPLE ---")
    print(simple_response.content)
    print("Provider:", simple_response.provider)

    hard_response = gateway.generate(
        "Explain the tradeoffs of event-driven architecture "
        "for a distributed payment system.",
        task=LLMTask.HARD,
    )

    print("\n--- HARD ---")
    print(hard_response.content)
    print("Provider:", hard_response.provider)

    agent_response = gateway.generate(
        "A customer says they were charged twice for order 123. "
        "Identify what the support agent should investigate.",
        task=LLMTask.AGENT,
    )

    print("\n--- AGENT ---")
    print(agent_response.content)
    print("Provider:", agent_response.provider)


if __name__ == "__main__":
    main()