import os

import httpx

from chatbot_platform.domain.entities.incoming_message import IncomingMessage
from chatbot_platform.domain.ports.channel_adapter import ChannelAdapter

_API_VERSION = "v21.0"
_BASE_URL = "https://graph.facebook.com"


class WhatsAppAdapter(ChannelAdapter):
    def __init__(
        self,
        phone_number_id: str,
        access_token: str,
        client: httpx.Client | None = None,
    ) -> None:
        self._phone_number_id = phone_number_id
        self._access_token = access_token
        self._client = client or httpx.Client()

    def parse_incoming(self, payload: dict) -> IncomingMessage | None:
        try:
            value = payload["entry"][0]["changes"][0]["value"]
            messages = value.get("messages")
            if not messages:
                return None

            message = messages[0]
            if message.get("type") != "text":
                return None

            return IncomingMessage(
                channel="whatsapp",
                external_user_id=message["from"],
                text=message["text"]["body"],
            )
        except (KeyError, IndexError, TypeError):
            return None

    def send_message(self, external_user_id: str, text: str) -> None:
        url = f"{_BASE_URL}/{_API_VERSION}/{self._phone_number_id}/messages"
        response = self._client.post(
            url,
            headers={"Authorization": f"Bearer {self._access_token}"},
            json={
                "messaging_product": "whatsapp",
                "to": external_user_id,
                "type": "text",
                "text": {"body": text},
            },
        )
        response.raise_for_status()


def create_whatsapp_adapter() -> WhatsAppAdapter:
    return WhatsAppAdapter(
        phone_number_id=os.environ["WHATSAPP_PHONE_NUMBER_ID"],
        access_token=os.environ["WHATSAPP_ACCESS_TOKEN"],
    )
