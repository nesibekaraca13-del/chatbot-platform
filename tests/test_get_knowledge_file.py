from pathlib import Path

import pytest

from chatbot_platform.application.use_cases.get_knowledge_file import get_knowledge_file_content


def test_returns_file_content(tmp_path: Path) -> None:
    (tmp_path / "faq.md").write_text("---\ncategory: faq\n---\n\n## Soru\n\nCevap\n", encoding="utf-8")

    content = get_knowledge_file_content(tmp_path, "faq.md")

    assert "## Soru" in content


def test_raises_for_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        get_knowledge_file_content(tmp_path, "yok.md")


def test_rejects_path_traversal(tmp_path: Path) -> None:
    secret = tmp_path.parent / "secret.md"
    secret.write_text("gizli", encoding="utf-8")

    with pytest.raises(ValueError):
        get_knowledge_file_content(tmp_path, "../secret.md")


def test_rejects_non_markdown_extension(tmp_path: Path) -> None:
    (tmp_path / "not_markdown.txt").write_text("veri", encoding="utf-8")

    with pytest.raises(ValueError):
        get_knowledge_file_content(tmp_path, "not_markdown.txt")
