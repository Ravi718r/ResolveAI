from app.ai.providers.base import LLMProvider
from app.ai.tasks import LLMTask


class ModelRouter:

    def __init__(
        self,
        qwen: LLMProvider,
        gpt_oss_120b: LLMProvider,
        gpt_oss_20b: LLMProvider,
    ):
        self.qwen = qwen
        self.gpt_oss_120b = gpt_oss_120b
        self.gpt_oss_20b = gpt_oss_20b

    def route(self, task: LLMTask) -> LLMProvider:
        """
        Return the primary model for a task.
        """

        if task == LLMTask.SIMPLE:
            return self.gpt_oss_20b

        if task == LLMTask.HARD:
            return self.gpt_oss_120b

        if task == LLMTask.AGENT:
            return self.qwen

        return self.qwen

    def fallback_chain(self, task: LLMTask) -> list[LLMProvider]:
        """
        Return models in the order they should be tried.
        """

        if task == LLMTask.SIMPLE:
            return [
                self.gpt_oss_20b,
                self.qwen,
                self.gpt_oss_120b,
            ]

        if task == LLMTask.HARD:
            return [
                self.gpt_oss_120b,
                self.qwen,
                self.gpt_oss_20b,
            ]

        # GENERAL and AGENT
        return [
            self.qwen,
            self.gpt_oss_120b,
            self.gpt_oss_20b,
        ]