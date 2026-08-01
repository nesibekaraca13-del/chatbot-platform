from pathlib import Path

from chatbot_platform.infrastructure.knowledge.markdown_loader import load_knowledge_base

KNOWLEDGE_DIR = Path(__file__).parent.parent / "tenants" / "default" / "knowledge"


def test_loads_all_knowledge_files() -> None:
    chunks = load_knowledge_base(KNOWLEDGE_DIR)
    assert len(chunks) > 0


def test_prices_chunks_have_correct_category() -> None:
    chunks = load_knowledge_base(KNOWLEDGE_DIR)
    price_chunks = [c for c in chunks if c.source_file == "prices.md"]
    assert len(price_chunks) == 2
    assert all(c.category == "prices" for c in price_chunks)
    assert {c.heading for c in price_chunks} == {"Paket 1", "Paket 2"}


def test_metadata_is_populated_from_frontmatter() -> None:
    chunks = load_knowledge_base(KNOWLEDGE_DIR)
    assert all(c.last_updated == "2026-07-22" for c in chunks)
    assert all(c.language == "tr" for c in chunks)
