import pytest
from fastapi.testclient import TestClient

from chatbot_platform.domain.entities.chat_message import ChatMessage
from chatbot_platform.domain.entities.incoming_message import IncomingMessage
from chatbot_platform.domain.entities.knowledge_chunk import KnowledgeChunk
from chatbot_platform.domain.ports.channel_adapter import ChannelAdapter
from chatbot_platform.domain.ports.conversation_repository import ConversationRepository
from chatbot_platform.domain.ports.llm_provider import LLMProvider
from chatbot_platform.domain.ports.vector_store import VectorStore
from chatbot_platform.interface.api.main import TenantRuntime, app, get_conversation_repository, get_tenant_runtime


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


@pytest.fixture()
def fake_adapter() -> _FakeChannelAdapter:
    return _FakeChannelAdapter()


@pytest.fixture(autouse=True)
def _override_dependencies(fake_adapter: _FakeChannelAdapter):
    fake_tenant = TenantRuntime(
        vector_store=_FakeVectorStore(),
        llm_provider=_FakeLLMProvider(),
        whatsapp_adapter=fake_adapter,
        instagram_adapter=fake_adapter,
        whatsapp_verify_token="expected-token",
        instagram_verify_token="ig-token",
    )
    app.dependency_overrides[get_tenant_runtime] = lambda: fake_tenant
    app.dependency_overrides[get_conversation_repository] = lambda: _FakeConversationRepository()
    yield fake_tenant
    app.dependency_overrides.clear()


client = TestClient(app)


def test_whatsapp_webhook_verification_succeeds_with_correct_token() -> None:
    response = client.get(
        "/t/firma-a/webhook/whatsapp",
        params={"hub.mode": "subscribe", "hub.verify_token": "expected-token", "hub.challenge": "12345"},
    )

    assert response.status_code == 200
    assert response.text == "12345"


def test_whatsapp_webhook_verification_fails_with_wrong_token() -> None:
    response = client.get(
        "/t/firma-a/webhook/whatsapp",
        params={"hub.mode": "subscribe", "hub.verify_token": "wrong", "hub.challenge": "12345"},
    )

    assert response.status_code == 403


def test_whatsapp_webhook_post_triggers_reply(fake_adapter: _FakeChannelAdapter) -> None:
    response = client.post("/t/firma-a/webhook/whatsapp", json={"text": "Merhaba"})

    assert response.status_code == 200
    assert fake_adapter.sent == [("user-1", "test cevabı")]


def test_instagram_webhook_verification_succeeds_with_correct_token() -> None:
    response = client.get(
        "/t/firma-a/webhook/instagram",
        params={"hub.mode": "subscribe", "hub.verify_token": "ig-token", "hub.challenge": "999"},
    )

    assert response.status_code == 200
    assert response.text == "999"


def test_instagram_webhook_post_triggers_reply(fake_adapter: _FakeChannelAdapter) -> None:
    response = client.post("/t/firma-a/webhook/instagram", json={"text": "Merhaba"})

    assert response.status_code == 200
    assert fake_adapter.sent == [("user-1", "test cevabı")]


def test_whatsapp_webhook_returns_503_when_not_configured() -> None:
    unconfigured_tenant = TenantRuntime(
        vector_store=_FakeVectorStore(),
        llm_provider=_FakeLLMProvider(),
        whatsapp_adapter=None,
        instagram_adapter=None,
        whatsapp_verify_token=None,
        instagram_verify_token=None,
    )
    app.dependency_overrides[get_tenant_runtime] = lambda: unconfigured_tenant

    response = client.post("/t/firma-a/webhook/whatsapp", json={"text": "Merhaba"})

    assert response.status_code == 503


def test_chat_returns_404_for_unknown_tenant_via_real_lookup() -> None:
    app.dependency_overrides.pop(get_tenant_runtime, None)
    app.state.tenants = {}

    response = client.get(
        "/t/olmayan-firma/webhook/whatsapp",
        params={"hub.mode": "subscribe", "hub.verify_token": "x", "hub.challenge": "1"},
    )

    assert response.status_code == 404
