from abc import ABC, abstractmethod

from chatbot_platform.domain.entities.incoming_message import IncomingMessage


class ChannelAdapter(ABC):
    @abstractmethod
    def parse_incoming(self, payload: dict) -> IncomingMessage | None: ...

    @abstractmethod
    def send_message(self, external_user_id: str, text: str) -> None: ...
