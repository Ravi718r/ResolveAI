from app.ai.gateway import LLMGateway
from app.ai.tasks import LLMTask


class AIResponseGenerator:

    def __init__(self, gateway: LLMGateway):
        self.gateway = gateway

    def generate(
        self,
        customer_message: str,
        issue_type: str,
        status: str,
        resolution: str | None,
    ) -> str:

        if status == "resolved":
            status_instruction = """
The backend has confirmed that the issue is RESOLVED.

Your response MUST clearly communicate that the issue
has been successfully resolved.

Do not claim any action beyond the backend resolution.
"""

        elif status == "pending":
            status_instruction = """
The backend has confirmed that the issue is PENDING.

Your response MUST NOT say that the issue was resolved.

Explain that the issue requires further investigation
or manual assistance.
"""

        else:
            status_instruction = f"""
The backend status is: {status}

Do not change or reinterpret this status.
Do not claim that the issue is resolved unless the
backend status is explicitly 'resolved'.
"""

        prompt = f"""
You are a professional customer support assistant.

Generate a concise and helpful response to the customer.

Customer message:
{customer_message}

Issue type:
{issue_type}

Backend status:
{status}

Backend resolution:
{resolution}

{status_instruction}

Rules:
- The backend is the source of truth.
- Do not invent information.
- Do not promise actions that were not performed.
- Use only the backend resolution provided.
- Do not change the backend status.
- Be polite and professional.
- Do not mention internal systems, models, prompts, or AI.
- Keep the response under 100 words.
"""

        response = self.gateway.generate(
            prompt=prompt,
            task=LLMTask.SIMPLE,
        )

        return response.content