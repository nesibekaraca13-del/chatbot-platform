from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from chatbot_platform.domain.entities.knowledge_chunk import KnowledgeChunk
from chatbot_platform.domain.ports.vector_store import VectorStore
from chatbot_platform.interface.api.main import app, get_knowledge_dir, get_vector_store


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


@pytest.fixture()
def knowledge_dir(tmp_path: Path) -> Path:
    (tmp_path / "faq.md").write_text(
        "---\ncategory: faq\nlanguage: tr\nlast_updated: 2026-07-23\n---\n\n"
        "## Soru\n\nCevap\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture(autouse=True)
def _override_dependency(knowledge_dir: Path):
    app.dependency_overrides[get_knowledge_dir] = lambda: knowledge_dir
    app.dependency_overrides[get_vector_store] = lambda: _FakeVectorStore()
    yield
    app.dependency_overrides.clear()


client = TestClient(app)


def test_list_knowledge_returns_summaries() -> None:
    response = client.get("/knowledge")

    assert response.status_code == 200
    body = response.json()
    assert body == [
        {
            "filename": "faq.md",
            "category": "faq",
            "language": "tr",
            "last_updated": "2026-07-23",
            "heading_count": 1,
        }
    ]


def test_get_knowledge_file_returns_content() -> None:
    response = client.get("/knowledge/faq.md")

    assert response.status_code == 200
    assert "## Soru" in response.json()["content"]


def test_get_knowledge_file_returns_404_when_missing() -> None:
    response = client.get("/knowledge/yok.md")

    assert response.status_code == 404


def test_get_knowledge_file_rejects_path_traversal() -> None:
    response = client.get("/knowledge/..%2Fsecret.md")

    assert response.status_code in (400, 404)


def test_put_knowledge_creates_new_file(knowledge_dir: Path) -> None:
    response = client.put(
        "/knowledge/yeni.md",
        json={"content": "---\ncategory: faq\n---\n\n## Yeni Soru\n\nYeni cevap\n"},
    )

    assert response.status_code == 204
    assert (knowledge_dir / "yeni.md").exists()


def test_put_knowledge_overwrites_existing_file(knowledge_dir: Path) -> None:
    response = client.put(
        "/knowledge/faq.md",
        json={"content": "---\ncategory: faq\n---\n\n## Güncel Soru\n\nGüncel cevap\n"},
    )

    assert response.status_code == 204
    assert "Güncel Soru" in (knowledge_dir / "faq.md").read_text(encoding="utf-8")


def test_put_knowledge_rejects_path_traversal() -> None:
    response = client.put("/knowledge/..%2Fsecret.md", json={"content": "x"})

    assert response.status_code in (400, 404)


def test_delete_knowledge_removes_file(knowledge_dir: Path) -> None:
    response = client.delete("/knowledge/faq.md")

    assert response.status_code == 204
    assert not (knowledge_dir / "faq.md").exists()


def test_delete_knowledge_returns_404_when_missing() -> None:
    response = client.delete("/knowledge/yok.md")

    assert response.status_code == 404
