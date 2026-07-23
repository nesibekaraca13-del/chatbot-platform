from pathlib import Path

from chatbot_platform.infrastructure.knowledge.markdown_loader import load_knowledge_base


def list_knowledge_files(knowledge_dir: Path) -> list[dict]:
    chunks = load_knowledge_base(knowledge_dir)

    files: dict[str, dict] = {}
    for chunk in chunks:
        info = files.setdefault(
            chunk.source_file,
            {
                "filename": chunk.source_file,
                "category": chunk.category,
                "language": chunk.language,
                "last_updated": chunk.last_updated,
                "heading_count": 0,
            },
        )
        info["heading_count"] += 1

    return sorted(files.values(), key=lambda f: f["filename"])
