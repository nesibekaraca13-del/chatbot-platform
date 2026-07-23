import sys
from pathlib import Path

from chatbot_platform.application.use_cases.generate_draft_knowledge import (
    generate_draft_knowledge_files,
)
from chatbot_platform.infrastructure.crawler.site_crawler import crawl_site

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
_DRAFTS_DIR = _PROJECT_ROOT / "knowledge_drafts"
_DEFAULT_MAX_PAGES = 20


def main() -> None:
    if len(sys.argv) < 2:
        print("Kullanım: python -m chatbot_platform.interface.cli.crawl <url> [max_sayfa]")
        return

    start_url = sys.argv[1]
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else _DEFAULT_MAX_PAGES

    print(f"{start_url} taranıyor (en fazla {max_pages} sayfa)...")
    pages = crawl_site(start_url, max_pages=max_pages)
    print(f"{len(pages)} sayfa indirildi.")

    written = generate_draft_knowledge_files(pages, _DRAFTS_DIR)
    print(f"{len(written)} taslak dosya oluşturuldu: {_DRAFTS_DIR}")
    for path in written:
        print(f"  - {path.name}")

    print("\nLütfen bu dosyaları gözden geçirin, gerekirse düzenleyin.")
    print("Onaylamak için: python -m chatbot_platform.interface.cli.approve <dosya.md> [...]")
    print("Tümünü onaylamak için: python -m chatbot_platform.interface.cli.approve --all")


if __name__ == "__main__":
    main()
