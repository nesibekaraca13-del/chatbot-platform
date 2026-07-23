from pathlib import Path

from chatbot_platform.application.use_cases.approve_draft_knowledge import (
    approve_draft_knowledge,
)
from chatbot_platform.domain.entities.knowledge_chunk import KnowledgeChunk
from chatbot_platform.domain.ports.vector_store import VectorStore


class _FakeVectorStore(VectorStore):
    def __init__(self) -> None:
        self.indexed: list[KnowledgeChunk] = []

    def index(self, chunks: list[KnowledgeChunk]) -> None:
        self.indexed = chunks

    def search(self, query: str, top_k: int = 3) -> list[KnowledgeChunk]:
        return []

    def count(self) -> int:
        return len(self.indexed)

    def clear(self) -> None:
        self.indexed = []


def _write_draft(path: Path, heading: str) -> None:
    path.write_text(
        "---\ncategory: taslak\nlanguage: tr\nlast_updated: 2026-07-23\n---\n\n"
        f"## {heading}\n\nmetin\n",
        encoding="utf-8",
    )


def test_approve_moves_draft_into_knowledge_dir_and_reindexes(tmp_path: Path) -> None:
    drafts_dir = tmp_path / "drafts"
    knowledge_dir = tmp_path / "knowledge"
    drafts_dir.mkdir()
    knowledge_dir.mkdir()

    draft_file = drafts_dir / "hakkimizda.md"
    _write_draft(draft_file, "Hakkımızda")

    vector_store = _FakeVectorStore()
    count = approve_draft_knowledge([draft_file], knowledge_dir, vector_store)

    assert not draft_file.exists()
    assert (knowledge_dir / "hakkimizda.md").exists()
    assert count == 1
    assert vector_store.indexed[0].heading == "Hakkımızda"


def test_approve_multiple_drafts(tmp_path: Path) -> None:
    drafts_dir = tmp_path / "drafts"
    knowledge_dir = tmp_path / "knowledge"
    drafts_dir.mkdir()
    knowledge_dir.mkdir()

    _write_draft(drafts_dir / "a.md", "A")
    _write_draft(drafts_dir / "b.md", "B")

    vector_store = _FakeVectorStore()
    count = approve_draft_knowledge(
        [drafts_dir / "a.md", drafts_dir / "b.md"], knowledge_dir, vector_store
    )

    assert count == 2
    assert {c.heading for c in vector_store.indexed} == {"A", "B"}
