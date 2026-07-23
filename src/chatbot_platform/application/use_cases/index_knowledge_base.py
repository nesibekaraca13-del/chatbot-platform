from pathlib import Path

from chatbot_platform.domain.ports.vector_store import VectorStore
from chatbot_platform.infrastructure.knowledge.markdown_loader import load_knowledge_base


def index_knowledge_base(knowledge_dir: Path, vector_store: VectorStore) -> int:
    chunks = load_knowledge_base(knowledge_dir)
    vector_store.clear()
    vector_store.index(chunks)
    return len(chunks)
