from pathlib import Path


def get_knowledge_file_content(knowledge_dir: Path, filename: str) -> str:
    resolved_dir = knowledge_dir.resolve()
    file_path = (knowledge_dir / filename).resolve()

    if file_path.parent != resolved_dir or not file_path.name.endswith(".md"):
        raise ValueError(f"Geçersiz dosya adı: {filename}")

    if not file_path.exists():
        raise FileNotFoundError(filename)

    return file_path.read_text(encoding="utf-8")
