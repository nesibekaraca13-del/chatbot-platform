import os

import httpx

from chatbot_platform.domain.entities.incoming_message import IncomingMessage
from chatbot_platform.domain.ports.channel_adapter import ChannelAdapter

_API_VERSION = "v21.0"
_BASE_URL = "https://graph.facebook.com"


class InstagramAdapter(ChannelAdapter):
    def __init__(
        self,
        ig_user_id: str,
        access_token: str,
        client: httpx.Client | None = None,
    ) -> None:
        self._ig_user_id = ig_user_id
        self._access_token = access_token
        self._client = client or httpx.Client()

    def parse_incoming(self, payload: dict) -> IncomingMessage | None:
        try:
            event = payload["entry"][0]["messaging"][0]
            message = event.get("message")
            if not message or "text" not in message or message.get("is_echo"):
                return None

            return IncomingMessage(
                channel="instagram",
                external_user_id=event["sender"]["id"],
                text=message["text"],
            )
        except (KeyError, IndexError, TypeError):
            return None

    def send_message(self, external_user_id: str, text: str) -> None:
        url = f"{_BASE_URL}/{_API_VERSION}/{self._ig_user_id}/messages"
        response = self._client.post(
            url,
            headers={"Authorization": f"Bearer {self._access_token}"},
            json={
                "recipient": {"id": external_user_id},
                "message": {"text": text},
            },
        )
        response.raise_for_status()


def create_instagram_adapter() -> InstagramAdapter:
    return InstagramAdapter(
        ig_user_id=os.environ["INSTAGRAM_IG_USER_ID"],
        access_token=os.environ["INSTAGRAM_ACCESS_TOKEN"],
    )
