import os

import pytest
from fastapi.testclient import TestClient

from chatbot_platform.domain.entities.chat_message import ChatMessage
from chatbot_platform.domain.entities.incoming_message import IncomingMessage
from chatbot_platform.domain.entities.knowledge_chunk import KnowledgeChunk
from chatbot_platform.domain.ports.channel_adapter import ChannelAdapter
from chatbot_platform.domain.ports.conversation_repository import ConversationRepository
from chatbot_platform.domain.ports.llm_provider import LLMProvider
from chatbot_platform.domain.ports.vector_store import VectorStore
from chatbot_platform.interface.api.main import (
    app,
    get_conversation_repository,
    get_instagram_adapter,
    get_llm_provider,
    get_vector_store,
    get_whatsapp_adapter,
)


class _FakeChannelAdapter(ChannelAdapter):
    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    def parse_incoming(self, payload: dict) -> IncomingMessage | None:
        if "text" not in payload:
            return None
        return IncomingMessage(channel="fake", external_user_id="user-1", text=payload["text"])

    def send_message(self, external_user_id: str, text: str) -> None:
        self.sent.append((external_user_id, text))


class _FakeVectorStore(VectorStore):
    def index(self, chunks: list[KnowledgeChunk]) -> None:
        pass

    def search(self, query: str, top_k: int = 3) -> list[KnowledgeChunk]:
        return []

    def count(self) -> int:
        return 0

    def clear(self) -> None:
        pass


class _FakeLLMProvider(LLMProvider):
    def generate(self, system_prompt: str, messages: list[ChatMessage]) -> str:
        return "test cevabı"


class _FakeConversationRepository(ConversationRepository):
    def get_history(self, conversation_id: str, limit: int = 20) -> list[ChatMessage]:
        return []

    def append_message(self, conversation_id: str, message: ChatMessage) -> None:
        pass


@pytest.fixture(autouse=True)
def _override_dependencies():
    fake_adapter = _FakeChannelAdapter()
    app.dependency_overrides[get_whatsapp_adapter] = lambda: fake_adapter
    app.dependency_overrides[get_instagram_adapter] = lambda: fake_adapter
    app.dependency_overrides[get_vector_store] = lambda: _FakeVectorStore()
    app.dependency_overrides[get_llm_provider] = lambda: _FakeLLMProvider()
    app.dependency_overrides[get_conversation_repository] = lambda: _FakeConversationRepository()
    yield fake_adapter
    app.dependency_overrides.clear()


client = TestClient(app)


def test_whatsapp_webhook_verification_succeeds_with_correct_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WHATSAPP_VERIFY_TOKEN", "expected-token")

    response = client.get(
        "/webhook/whatsapp",
        params={"hub.mode": "subscribe", "hub.verify_token": "expected-token", "hub.challenge": "12345"},
    )

    assert response.status_code == 200
    assert response.text == "12345"


def test_whatsapp_webhook_verification_fails_with_wrong_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WHATSAPP_VERIFY_TOKEN", "expected-token")

    response = client.get(
        "/webhook/whatsapp",
        params={"hub.mode": "subscribe", "hub.verify_token": "wrong", "hub.challenge": "12345"},
    )

    assert response.status_code == 403


def test_whatsapp_webhook_post_triggers_reply(_override_dependencies) -> None:
    response = client.post("/webhook/whatsapp", json={"text": "Merhaba"})

    assert response.status_code == 200
    assert _override_dependencies.sent == [("user-1", "test cevabı")]


def test_instagram_webhook_verification_succeeds_with_correct_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INSTAGRAM_VERIFY_TOKEN", "ig-token")

    response = client.get(
        "/webhook/instagram",
        params={"hub.mode": "subscribe", "hub.verify_token": "ig-token", "hub.challenge": "999"},
    )

    assert response.status_code == 200
    assert response.text == "999"


def test_instagram_webhook_post_triggers_reply(_override_dependencies) -> None:
    response = client.post("/webhook/instagram", json={"text": "Merhaba"})

    assert response.status_code == 200
    assert _override_dependencies.sent == [("user-1", "test cevabı")]


def test_whatsapp_webhook_returns_503_when_not_configured() -> None:
    app.dependency_overrides.pop(get_whatsapp_adapter, None)

    def _raise_unconfigured():
        from fastapi import HTTPException

        raise HTTPException(status_code=503, detail="WhatsApp yapılandırılmamış")

    app.dependency_overrides[get_whatsapp_adapter] = _raise_unconfigured

    response = client.post("/webhook/whatsapp", json={"text": "Merhaba"})

    assert response.status_code == 503
