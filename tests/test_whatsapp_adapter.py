import json

import httpx
import pytest

from chatbot_platform.infrastructure.channels.whatsapp_adapter import WhatsAppAdapter

_SAMPLE_TEXT_PAYLOAD = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "123",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {"phone_number_id": "PHONE_ID"},
                        "messages": [
                            {
                                "from": "905551234567",
                                "id": "wamid.abc",
                                "timestamp": "1234567890",
                                "type": "text",
                                "text": {"body": "Merhaba"},
                            }
                        ],
                    },
                    "field": "messages",
                }
            ],
        }
    ],
}

_SAMPLE_STATUS_PAYLOAD = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "123",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "statuses": [{"id": "wamid.abc", "status": "delivered"}],
                    },
                    "field": "messages",
                }
            ],
        }
    ],
}


def test_parse_incoming_extracts_text_message() -> None:
    adapter = WhatsAppAdapter(phone_number_id="PHONE_ID", access_token="token")

    message = adapter.parse_incoming(_SAMPLE_TEXT_PAYLOAD)

    assert message is not None
    assert message.channel == "whatsapp"
    assert message.external_user_id == "905551234567"
    assert message.text == "Merhaba"


def test_parse_incoming_ignores_status_updates() -> None:
    adapter = WhatsAppAdapter(phone_number_id="PHONE_ID", access_token="token")

    assert adapter.parse_incoming(_SAMPLE_STATUS_PAYLOAD) is None


def test_parse_incoming_returns_none_for_malformed_payload() -> None:
    adapter = WhatsAppAdapter(phone_number_id="PHONE_ID", access_token="token")

    assert adapter.parse_incoming({"unexpected": "shape"}) is None


def test_send_message_posts_to_graph_api() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["headers"] = dict(request.headers)
        captured["body"] = json.loads(request.read())
        return httpx.Response(200, json={"messages": [{"id": "wamid.reply"}]})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    adapter = WhatsAppAdapter(
        phone_number_id="PHONE_ID", access_token="secret-token", client=client
    )

    adapter.send_message("905551234567", "Merhaba, size nasıl yardımcı olabilirim?")

    assert "PHONE_ID/messages" in captured["url"]
    assert captured["headers"]["authorization"] == "Bearer secret-token"
    assert captured["body"]["to"] == "905551234567"
    assert captured["body"]["text"]["body"] == "Merhaba, size nasıl yardımcı olabilirim?"


def test_send_message_raises_on_error_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"error": {"message": "invalid token"}})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    adapter = WhatsAppAdapter(phone_number_id="PHONE_ID", access_token="bad", client=client)

    with pytest.raises(httpx.HTTPStatusError):
        adapter.send_message("905551234567", "test")
