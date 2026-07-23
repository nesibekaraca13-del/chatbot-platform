from pathlib import Path

from chatbot_platform.application.use_cases.list_knowledge_files import list_knowledge_files


def _write(path: Path, category: str, headings: list[str]) -> None:
    body = "\n\n".join(f"## {h}\n\nmetin" for h in headings)
    path.write_text(
        f"---\ncategory: {category}\nlanguage: tr\nlast_updated: 2026-07-23\n---\n\n{body}\n",
        encoding="utf-8",
    )


def test_list_knowledge_files_summarizes_each_file(tmp_path: Path) -> None:
    _write(tmp_path / "prices.md", "prices", ["Paket 1", "Paket 2"])
    _write(tmp_path / "faq.md", "faq", ["Soru 1"])

    files = list_knowledge_files(tmp_path)

    assert files == [
        {
            "filename": "faq.md",
            "category": "faq",
            "language": "tr",
            "last_updated": "2026-07-23",
            "heading_count": 1,
        },
        {
            "filename": "prices.md",
            "category": "prices",
            "language": "tr",
            "last_updated": "2026-07-23",
            "heading_count": 2,
        },
    ]
