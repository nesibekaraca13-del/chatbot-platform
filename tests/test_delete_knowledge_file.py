from pathlib import Path

import pytest

from chatbot_platform.application.use_cases.delete_knowledge_file import delete_knowledge_file
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


def test_delete_knowledge_file_removes_file_and_reindexes(tmp_path: Path) -> None:
    (tmp_path / "faq.md").write_text(
        "---\ncategory: faq\n---\n\n## Soru\n\nCevap\n", encoding="utf-8"
    )
    (tmp_path / "prices.md").write_text(
        "---\ncategory: prices\n---\n\n## Paket\n\nFiyat\n", encoding="utf-8"
    )
    vector_store = _FakeVectorStore()

    delete_knowledge_file(tmp_path, "faq.md", vector_store)

    assert not (tmp_path / "faq.md").exists()
    assert vector_store.count() == 1
    assert vector_store.indexed[0].heading == "Paket"


def test_delete_knowledge_file_raises_for_missing_file(tmp_path: Path) -> None:
    vector_store = _FakeVectorStore()

    with pytest.raises(FileNotFoundError):
        delete_knowledge_file(tmp_path, "yok.md", vector_store)
