from pathlib import Path

from chatbot_platform.infrastructure.knowledge.safe_path import resolve_knowledge_file_path


def get_knowledge_file_content(knowledge_dir: Path, filename: str) -> str:
    file_path = resolve_knowledge_file_path(knowledge_dir, filename)

    if not file_path.exists():
        raise FileNotFoundError(filename)

    return file_path.read_text(encoding="utf-8")
