from app.ai.classifier import SupportClassifier
from app.ai.llm import create_llm_gateway


def main():

    gateway = create_llm_gateway()

    classifier = SupportClassifier(gateway)

    result = classifier.classify(
        "I was charged twice for order 123."
    )

    print("\n--- CLASSIFICATION ---")
    print("Issue type:", result.issue_type)
    print("Order ID:", result.order_id)
    print("Confidence:", result.confidence)


if __name__ == "__main__":
    main()