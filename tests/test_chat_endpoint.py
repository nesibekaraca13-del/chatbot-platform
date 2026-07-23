import pytest
from fastapi.testclient import TestClient

from chatbot_platform.domain.entities.chat_message import ChatMessage
from chatbot_platform.domain.entities.knowledge_chunk import KnowledgeChunk
from chatbot_platform.domain.ports.conversation_repository import ConversationRepository
from chatbot_platform.domain.ports.llm_provider import LLMProvider
from chatbot_platform.domain.ports.vector_store import VectorStore
from chatbot_platform.interface.api.main import (
    app,
    get_conversation_repository,
    get_llm_provider,
    get_vector_store,
)


class _FakeVectorStore(VectorStore):
    def index(self, chunks: list[KnowledgeChunk]) -> None:
        raise NotImplementedError

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
    def __init__(self) -> None:
        self._messages: dict[str, list[ChatMessage]] = {}

    def get_history(self, conversation_id: str, limit: int = 20) -> list[ChatMessage]:
        return self._messages.get(conversation_id, [])[-limit:]

    def append_message(self, conversation_id: str, message: ChatMessage) -> None:
        self._messages.setdefault(conversation_id, []).append(message)


@pytest.fixture(autouse=True)
def _override_dependencies() -> None:
    app.dependency_overrides[get_vector_store] = lambda: _FakeVectorStore()
    app.dependency_overrides[get_llm_provider] = lambda: _FakeLLMProvider()
    app.dependency_overrides[get_conversation_repository] = lambda: _FakeConversationRepository()
    yield
    app.dependency_overrides.clear()


client = TestClient(app)


def test_chat_returns_answer_and_generates_conversation_id() -> None:
    response = client.post("/chat", json={"message": "Merhaba"})

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "test cevabı"
    assert body["conversation_id"]


def test_chat_reuses_provided_conversation_id() -> None:
    response = client.post(
        "/chat", json={"message": "Merhaba", "conversation_id": "conv-abc"}
    )

    assert response.json()["conversation_id"] == "conv-abc"
