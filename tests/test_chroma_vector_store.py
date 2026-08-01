from pathlib import Path

from chatbot_platform.application.use_cases.index_knowledge_base import index_knowledge_base
from chatbot_platform.infrastructure.vector_store.chroma_vector_store import ChromaVectorStore

KNOWLEDGE_DIR = Path(__file__).parent.parent / "tenants" / "default" / "knowledge"


def test_index_populates_the_store(tmp_path: Path) -> None:
    store = ChromaVectorStore(persist_directory=tmp_path)
    indexed_count = index_knowledge_base(KNOWLEDGE_DIR, store)

    assert indexed_count > 0
    assert store.count() == indexed_count


def test_reindexing_does_not_duplicate(tmp_path: Path) -> None:
    store = ChromaVectorStore(persist_directory=tmp_path)
    index_knowledge_base(KNOWLEDGE_DIR, store)
    first_count = store.count()

    index_knowledge_base(KNOWLEDGE_DIR, store)

    assert store.count() == first_count


def test_search_returns_relevant_category(tmp_path: Path) -> None:
    store = ChromaVectorStore(persist_directory=tmp_path)
    index_knowledge_base(KNOWLEDGE_DIR, store)

    results = store.search("fiyat paketleri nelerdir", top_k=3)

    assert len(results) == 3
    assert any(chunk.category == "prices" for chunk in results)


def test_clear_removes_all_indexed_chunks(tmp_path: Path) -> None:
    store = ChromaVectorStore(persist_directory=tmp_path)
    index_knowledge_base(KNOWLEDGE_DIR, store)
    assert store.count() > 0

    store.clear()

    assert store.count() == 0
