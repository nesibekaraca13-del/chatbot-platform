from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from chatbot_platform.infrastructure.crawler.text_extractor import extract_clean_text, extract_title

_DEFAULT_CATEGORY = "taslak"
_DEFAULT_LANGUAGE = "tr"


def generate_draft_knowledge_files(pages: dict[str, str], output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written_files: list[Path] = []
    used_filenames: set[str] = set()

    for url, html in pages.items():
        text = extract_clean_text(html)
        if not text:
            continue

        title = extract_title(html) or url
        filename = _slugify_url(url, used_filenames)
        used_filenames.add(filename)

        file_path = output_dir / f"{filename}.md"
        file_path.write_text(_render_draft(title=title, text=text, source_url=url), encoding="utf-8")
        written_files.append(file_path)

    return written_files


def _slugify_url(url: str, used: set[str]) -> str:
    path = urlparse(url).path.strip("/")
    slug = "".join(c if c.isalnum() else "-" for c in path).strip("-").lower()
    slug = slug or "home"

    candidate = slug
    counter = 2
    while candidate in used:
        candidate = f"{slug}-{counter}"
        counter += 1
    return candidate


def _render_draft(title: str, text: str, source_url: str) -> str:
    frontmatter = (
        "---\n"
        f"category: {_DEFAULT_CATEGORY}\n"
        f"language: {_DEFAULT_LANGUAGE}\n"
        f"last_updated: {date.today().isoformat()}\n"
        f"source_url: {source_url}\n"
        "---\n\n"
    )
    return f"{frontmatter}## {title}\n\n{text}\n"
