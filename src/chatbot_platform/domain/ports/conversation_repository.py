from abc import ABC, abstractmethod

from chatbot_platform.domain.entities.chat_message import ChatMessage


class ConversationRepository(ABC):
    @abstractmethod
    def get_history(self, conversation_id: str, limit: int = 20) -> list[ChatMessage]: ...

    @abstractmethod
    def append_message(self, conversation_id: str, message: ChatMessage) -> None: ...
