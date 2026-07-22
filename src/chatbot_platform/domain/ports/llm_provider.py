from abc import ABC, abstractmethod

from chatbot_platform.domain.entities.chat_message import ChatMessage


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, messages: list[ChatMessage]) -> str: ...
