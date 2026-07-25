from dataclasses import dataclass


@dataclass(frozen=True)
class IncomingMessage:
    channel: str
    external_user_id: str
    text: str
