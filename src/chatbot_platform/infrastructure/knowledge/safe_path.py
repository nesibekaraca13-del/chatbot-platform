from pathlib import Path


def resolve_knowledge_file_path(knowledge_dir: Path, filename: str) -> Path:
    resolved_dir = knowledge_dir.resolve()
    file_path = (knowledge_dir / filename).resolve()

    if file_path.parent != resolved_dir or not file_path.name.endswith(".md"):
        raise ValueError(f"Geçersiz dosya adı: {filename}")

    return file_path
