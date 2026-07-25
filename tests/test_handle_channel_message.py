from pathlib import Path

from chatbot_platform.application.use_cases.handle_channel_message import (
    handle_channel_message,
)
from chatbot_platform.domain.entities.chat_message import ChatMessage
from chatbot_platform.domain.entities.incoming_message import IncomingMessage
from chatbot_platform.domain.entities.knowledge_chunk import KnowledgeChunk
from chatbot_platform.domain.ports.channel_adapter import ChannelAdapter
from chatbot_platform.domain.ports.llm_provider import LLMProvider
from chatbot_platform.domain.ports.vector_store import VectorStore
from chatbot_platform.infrastructure.persistence.sqlite_conversation_repository import (
    SqliteConversationRepository,
)

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


class _FakeChannelAdapter(ChannelAdapter):
    def __init__(self, incoming: IncomingMessage | None) -> None:
        self._incoming = incoming
        self.sent: list[tuple[str, str]] = []

    def parse_incoming(self, payload: dict) -> IncomingMessage | None:
        return self._incoming

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
        return "Merhaba, size nasıl yardımcı olabilirim?"


def test_handle_channel_message_sends_reply_back_through_adapter(tmp_path: Path) -> None:
    incoming = IncomingMessage(channel="whatsapp", external_user_id="905551234567", text="Merhaba")
    adapter = _FakeChannelAdapter(incoming)
    conversation_repository = SqliteConversationRepository(tmp_path / "test.db")

    handled = handle_channel_message(
        {"any": "payload"},
        adapter,
        _FakeVectorStore(),
        _FakeLLMProvider(),
        PROMPTS_DIR,
        conversation_repository,
    )

    assert handled is True
    assert adapter.sent == [("905551234567", "Merhaba, size nasıl yardımcı olabilirim?")]


def test_handle_channel_message_uses_channel_and_user_as_conversation_id(tmp_path: Path) -> None:
    incoming = IncomingMessage(channel="whatsapp", external_user_id="905551234567", text="Merhaba")
    adapter = _FakeChannelAdapter(incoming)
    conversation_repository = SqliteConversationRepository(tmp_path / "test.db")

    handle_channel_message(
        {}, adapter, _FakeVectorStore(), _FakeLLMProvider(), PROMPTS_DIR, conversation_repository
    )

    history = conversation_repository.get_history("whatsapp:905551234567")
    assert len(history) == 2


def test_handle_channel_message_ignores_unparseable_payload(tmp_path: Path) -> None:
    adapter = _FakeChannelAdapter(None)
    conversation_repository = SqliteConversationRepository(tmp_path / "test.db")

    handled = handle_channel_message(
        {}, adapter, _FakeVectorStore(), _FakeLLMProvider(), PROMPTS_DIR, conversation_repository
    )

    assert handled is False
    assert adapter.sent == []
