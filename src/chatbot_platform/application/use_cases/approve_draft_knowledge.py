from pathlib import Path

from chatbot_platform.application.use_cases.index_knowledge_base import index_knowledge_base
from chatbot_platform.domain.ports.vector_store import VectorStore


def approve_draft_knowledge(
    draft_paths: list[Path],
    knowledge_dir: Path,
    vector_store: VectorStore,
) -> int:
    for draft_path in draft_paths:
        target_path = knowledge_dir / draft_path.name
        draft_path.replace(target_path)

    return index_knowledge_base(knowledge_dir, vector_store)
