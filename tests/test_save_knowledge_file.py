from pathlib import Path

from chatbot_platform.application.use_cases.save_knowledge_file import save_knowledge_file
from chatbot_platform.domain.entities.knowledge_chunk import KnowledgeChunk
from chatbot_platform.domain.ports.vector_store import VectorStore


class _FakeVectorStore(VectorStore):
    def __init__(self) -> None:
        self.indexed: list[KnowledgeChunk] = []

    def index(self, chunks: list[KnowledgeChunk]) -> None:
        self.indexed = list(chunks)

    def search(self, query: str, top_k: int = 3) -> list[KnowledgeChunk]:
        return []

    def count(self) -> int:
        return len(self.indexed)

    def clear(self) -> None:
        self.indexed = []


def test_save_knowledge_file_writes_content_and_reindexes(tmp_path: Path) -> None:
    vector_store = _FakeVectorStore()

    save_knowledge_file(
        tmp_path,
        "yeni.md",
        "---\ncategory: faq\nlanguage: tr\nlast_updated: 2026-07-23\n---\n\n## Soru\n\nCevap\n",
        vector_store,
    )

    assert (tmp_path / "yeni.md").read_text(encoding="utf-8").startswith("---")
    assert vector_store.count() == 1
    assert vector_store.indexed[0].heading == "Soru"


def test_save_knowledge_file_overwrites_existing_content(tmp_path: Path) -> None:
    (tmp_path / "faq.md").write_text(
        "---\ncategory: faq\n---\n\n## Eski\n\nEski metin\n", encoding="utf-8"
    )
    vector_store = _FakeVectorStore()

    save_knowledge_file(
        tmp_path,
        "faq.md",
        "---\ncategory: faq\n---\n\n## Yeni\n\nYeni metin\n",
        vector_store,
    )

    assert vector_store.indexed[0].heading == "Yeni"
