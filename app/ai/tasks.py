from enum import Enum


class LLMTask(str, Enum):
    SIMPLE = "simple"
    GENERAL = "general"
    HARD = "hard"
    AGENT = "agent"