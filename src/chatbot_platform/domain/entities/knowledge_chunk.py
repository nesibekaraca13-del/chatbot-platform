from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeChunk:
    text: str
    heading: str
    category: str
    language: str
    last_updated: str
    source_file: str
