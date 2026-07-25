from chatbot_platform.domain.entities.incoming_message import IncomingMessage
from chatbot_platform.domain.ports.channel_adapter import ChannelAdapter


class _FakeChannelAdapter(ChannelAdapter):
    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    def parse_incoming(self, payload: dict) -> IncomingMessage | None:
        if "text" not in payload or "from" not in payload:
            return None
        return IncomingMessage(
            channel="fake", external_user_id=payload["from"], text=payload["text"]
        )

    def send_message(self, external_user_id: str, text: str) -> None:
        self.sent.append((external_user_id, text))


def test_parse_incoming_returns_normalized_message() -> None:
    adapter = _FakeChannelAdapter()

    message = adapter.parse_incoming({"from": "user-1", "text": "Merhaba"})

    assert message == IncomingMessage(channel="fake", external_user_id="user-1", text="Merhaba")


def test_parse_incoming_returns_none_for_unrecognized_payload() -> None:
    adapter = _FakeChannelAdapter()

    assert adapter.parse_incoming({"unrelated": "data"}) is None


def test_send_message_records_call() -> None:
    adapter = _FakeChannelAdapter()

    adapter.send_message("user-1", "Merhaba, size nasıl yardımcı olabilirim?")

    assert adapter.sent == [("user-1", "Merhaba, size nasıl yardımcı olabilirim?")]
