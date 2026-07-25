import json

import httpx
import pytest

from chatbot_platform.infrastructure.channels.instagram_adapter import InstagramAdapter

_SAMPLE_TEXT_PAYLOAD = {
    "object": "instagram",
    "entry": [
        {
            "id": "PAGE_ID",
            "time": 1234567890,
            "messaging": [
                {
                    "sender": {"id": "IG_USER_123"},
                    "recipient": {"id": "PAGE_ID"},
                    "timestamp": 1234567890,
                    "message": {"mid": "msg.abc", "text": "Merhaba"},
                }
            ],
        }
    ],
}

_SAMPLE_ECHO_PAYLOAD = {
    "object": "instagram",
    "entry": [
        {
            "id": "PAGE_ID",
            "messaging": [
                {
                    "sender": {"id": "PAGE_ID"},
                    "recipient": {"id": "IG_USER_123"},
                    "message": {"mid": "msg.echo", "text": "Bizim cevabımız", "is_echo": True},
                }
            ],
        }
    ],
}


def test_parse_incoming_extracts_text_message() -> None:
    adapter = InstagramAdapter(ig_user_id="IG_ID", access_token="token")

    message = adapter.parse_incoming(_SAMPLE_TEXT_PAYLOAD)

    assert message is not None
    assert message.channel == "instagram"
    assert message.external_user_id == "IG_USER_123"
    assert message.text == "Merhaba"


def test_parse_incoming_ignores_echo_messages() -> None:
    adapter = InstagramAdapter(ig_user_id="IG_ID", access_token="token")

    assert adapter.parse_incoming(_SAMPLE_ECHO_PAYLOAD) is None


def test_parse_incoming_returns_none_for_malformed_payload() -> None:
    adapter = InstagramAdapter(ig_user_id="IG_ID", access_token="token")

    assert adapter.parse_incoming({"unexpected": "shape"}) is None


def test_send_message_posts_to_graph_api() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["headers"] = dict(request.headers)
        captured["body"] = json.loads(request.read())
        return httpx.Response(200, json={"message_id": "msg.reply"})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    adapter = InstagramAdapter(ig_user_id="IG_ID", access_token="secret-token", client=client)

    adapter.send_message("IG_USER_123", "Merhaba, size nasıl yardımcı olabilirim?")

    assert "IG_ID/messages" in captured["url"]
    assert captured["headers"]["authorization"] == "Bearer secret-token"
    assert captured["body"]["recipient"]["id"] == "IG_USER_123"
    assert captured["body"]["message"]["text"] == "Merhaba, size nasıl yardımcı olabilirim?"


def test_send_message_raises_on_error_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"error": {"message": "invalid token"}})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    adapter = InstagramAdapter(ig_user_id="IG_ID", access_token="bad", client=client)

    with pytest.raises(httpx.HTTPStatusError):
        adapter.send_message("IG_USER_123", "test")
