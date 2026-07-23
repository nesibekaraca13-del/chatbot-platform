from pathlib import Path

from chatbot_platform.application.use_cases.index_knowledge_base import index_knowledge_base
from chatbot_platform.domain.ports.vector_store import VectorStore
from chatbot_platform.infrastructure.knowledge.safe_path import resolve_knowledge_file_path


def delete_knowledge_file(
    knowledge_dir: Path,
    filename: str,
    vector_store: VectorStore,
) -> None:
    file_path = resolve_knowledge_file_path(knowledge_dir, filename)

    if not file_path.exists():
        raise FileNotFoundError(filename)

    file_path.unlink()
    index_knowledge_base(knowledge_dir, vector_store)
