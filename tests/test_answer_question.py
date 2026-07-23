from pathlib import Path

from chatbot_platform.application.use_cases.answer_question import answer_question
from chatbot_platform.domain.entities.chat_message import ChatMessage
from chatbot_platform.domain.entities.knowledge_chunk import KnowledgeChunk
from chatbot_platform.domain.ports.llm_provider import LLMProvider
from chatbot_platform.domain.ports.vector_store import VectorStore

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


class _FakeVectorStore(VectorStore):
    def __init__(self, chunks: list[KnowledgeChunk]) -> None:
        self._chunks = chunks
        self.last_query = ""

    def index(self, chunks: list[KnowledgeChunk]) -> None:
        raise NotImplementedError

    def search(self, query: str, top_k: int = 3) -> list[KnowledgeChunk]:
        self.last_query = query
        return self._chunks[:top_k]

    def count(self) -> int:
        return len(self._chunks)


class _FakeLLMProvider(LLMProvider):
    def __init__(self, response_text: str) -> None:
        self._response_text = response_text
        self.last_system_prompt = ""
        self.last_messages: list[ChatMessage] = []

    def generate(self, system_prompt: str, messages: list[ChatMessage]) -> str:
        self.last_system_prompt = system_prompt
        self.last_messages = messages
        return self._response_text


def _make_chunk(text: str, heading: str, source_file: str = "faq.md") -> KnowledgeChunk:
    return KnowledgeChunk(
        text=text,
        heading=heading,
        category="faq",
        language="tr",
        last_updated="2026-07-22",
        source_file=source_file,
    )


def test_answer_question_includes_retrieved_context_in_prompt() -> None:
    chunk = _make_chunk("Aylık paketimiz 1000 TL'dir.", "Paket 1", "prices.md")
    vector_store = _FakeVectorStore([chunk])
    llm_provider = _FakeLLMProvider("Aylık paketimiz 1000 TL.")

    answer = answer_question("Fiyatınız nedir?", vector_store, llm_provider, PROMPTS_DIR)

    assert answer == "Aylık paketimiz 1000 TL."
    assert "1000 TL" in llm_provider.last_system_prompt
    assert llm_provider.last_messages == [ChatMessage(role="user", content="Fiyatınız nedir?")]
    assert vector_store.last_query == "Fiyatınız nedir?"


def test_answer_question_respects_top_k() -> None:
    chunks = [_make_chunk(f"metin {i}", f"h{i}") for i in range(5)]
    vector_store = _FakeVectorStore(chunks)
    llm_provider = _FakeLLMProvider("cevap")

    answer_question("soru", vector_store, llm_provider, PROMPTS_DIR, top_k=2)

    assert "metin 0" in llm_provider.last_system_prompt
    assert "metin 1" in llm_provider.last_system_prompt
    assert "metin 2" not in llm_provider.last_system_prompt
