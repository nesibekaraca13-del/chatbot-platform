from pathlib import Path

import chromadb
from chromadb.config import Settings

from chatbot_platform.domain.entities.knowledge_chunk import KnowledgeChunk
from chatbot_platform.domain.ports.vector_store import VectorStore

_DEFAULT_COLLECTION = "knowledge_base"


class ChromaVectorStore(VectorStore):
    def __init__(
        self,
        persist_directory: Path,
        collection_name: str = _DEFAULT_COLLECTION,
    ) -> None:
        client = chromadb.PersistentClient(
            path=str(persist_directory),
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = client.get_or_create_collection(collection_name)

    def index(self, chunks: list[KnowledgeChunk]) -> None:
        if not chunks:
            return
        self._collection.upsert(
            ids=[self._chunk_id(chunk) for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            metadatas=[
                {
                    "heading": chunk.heading,
                    "category": chunk.category,
                    "language": chunk.language,
                    "last_updated": chunk.last_updated,
                    "source_file": chunk.source_file,
                }
                for chunk in chunks
            ],
        )

    def search(self, query: str, top_k: int = 3) -> list[KnowledgeChunk]:
        result = self._collection.query(query_texts=[query], n_results=top_k)
        documents = result["documents"][0] if result["documents"] else []
        metadatas = result["metadatas"][0] if result["metadatas"] else []
        return [
            KnowledgeChunk(
                text=document,
                heading=str(metadata["heading"]),
                category=str(metadata["category"]),
                language=str(metadata["language"]),
                last_updated=str(metadata["last_updated"]),
                source_file=str(metadata["source_file"]),
            )
            for document, metadata in zip(documents, metadatas)
        ]

    def count(self) -> int:
        return self._collection.count()

    def clear(self) -> None:
        existing_ids = self._collection.get()["ids"]
        if existing_ids:
            self._collection.delete(ids=existing_ids)

    @staticmethod
    def _chunk_id(chunk: KnowledgeChunk) -> str:
        return f"{chunk.source_file}::{chunk.heading}"
