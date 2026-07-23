from pathlib import Path

from chatbot_platform.application.use_cases.generate_draft_knowledge import (
    generate_draft_knowledge_files,
)
from chatbot_platform.infrastructure.knowledge.markdown_loader import load_knowledge_base


def test_generates_one_file_per_page(tmp_path: Path) -> None:
    pages = {
        "https://example.com/": (
            "<html><head><title>Ana Sayfa</title></head>"
            "<body><p>Hoş geldiniz.</p></body></html>"
        ),
        "https://example.com/hakkimizda": (
            "<html><head><title>Hakkımızda</title></head>"
            "<body><p>Biz kaliteliyiz.</p></body></html>"
        ),
    }

    written = generate_draft_knowledge_files(pages, tmp_path)

    assert len(written) == 2
    filenames = {f.name for f in written}
    assert filenames == {"home.md", "hakkimizda.md"}


def test_draft_file_has_valid_frontmatter_and_is_loadable(tmp_path: Path) -> None:
    pages = {
        "https://example.com/hizmetler": (
            "<html><head><title>Hizmetlerimiz</title></head>"
            "<body><p>Danışmanlık sunuyoruz.</p></body></html>"
        )
    }

    generate_draft_knowledge_files(pages, tmp_path)
    chunks = load_knowledge_base(tmp_path)

    assert len(chunks) == 1
    assert chunks[0].heading == "Hizmetlerimiz"
    assert "Danışmanlık sunuyoruz." in chunks[0].text
    assert chunks[0].category == "taslak"


def test_skips_pages_with_no_extractable_text(tmp_path: Path) -> None:
    pages = {"https://example.com/empty": "<html><body><script>x=1</script></body></html>"}

    written = generate_draft_knowledge_files(pages, tmp_path)

    assert written == []


def test_deduplicates_filenames_from_similar_urls(tmp_path: Path) -> None:
    pages = {
        "https://example.com/about": (
            "<html><head><title>A</title></head><body><p>metin bir</p></body></html>"
        ),
        "https://example.com/about/": (
            "<html><head><title>B</title></head><body><p>metin iki</p></body></html>"
        ),
    }

    written = generate_draft_knowledge_files(pages, tmp_path)

    names = sorted(f.name for f in written)
    assert names == ["about-2.md", "about.md"]
