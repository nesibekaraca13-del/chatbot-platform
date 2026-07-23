import sys
from pathlib import Path

from dotenv import load_dotenv

from chatbot_platform.application.use_cases.approve_draft_knowledge import (
    approve_draft_knowledge,
)
from chatbot_platform.infrastructure.vector_store.chroma_vector_store import ChromaVectorStore

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
_DRAFTS_DIR = _PROJECT_ROOT / "knowledge_drafts"
_KNOWLEDGE_DIR = _PROJECT_ROOT / "knowledge"
_CHROMA_DIR = _PROJECT_ROOT / "chroma_db"


def main() -> None:
    load_dotenv(_PROJECT_ROOT / ".env")

    args = sys.argv[1:]
    if not args:
        print("Kullanım: python -m chatbot_platform.interface.cli.approve <dosya1.md> [dosya2.md ...]")
        print("Ya da tüm taslakları onaylamak için: --all")
        return

    if args == ["--all"]:
        draft_paths = sorted(_DRAFTS_DIR.glob("*.md"))
    else:
        draft_paths = [_DRAFTS_DIR / name for name in args]

    missing = [p.name for p in draft_paths if not p.exists()]
    for name in missing:
        print(f"Uyarı: {name} taslak klasöründe bulunamadı, atlandı.")
    draft_paths = [p for p in draft_paths if p.exists()]

    if not draft_paths:
        print("Onaylanan dosya yok.")
        return

    vector_store = ChromaVectorStore(persist_directory=_CHROMA_DIR)
    count = approve_draft_knowledge(draft_paths, _KNOWLEDGE_DIR, vector_store)

    print(f"Onaylandı: {', '.join(p.name for p in draft_paths)}")
    print(f"Yeniden indexlendi: toplam {count} bilgi kartı.")


if __name__ == "__main__":
    main()
