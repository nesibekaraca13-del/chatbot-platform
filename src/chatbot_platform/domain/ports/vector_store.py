from abc import ABC, abstractmethod

from chatbot_platform.domain.entities.knowledge_chunk import KnowledgeChunk


class VectorStore(ABC):
    @abstractmethod
    def index(self, chunks: list[KnowledgeChunk]) -> None: ...

    @abstractmethod
    def search(self, query: str, top_k: int = 3) -> list[KnowledgeChunk]: ...

    @abstractmethod
    def count(self) -> int: ...
