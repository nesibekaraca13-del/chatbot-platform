from pathlib import Path

import yaml

from chatbot_platform.domain.entities.knowledge_chunk import KnowledgeChunk

_FRONTMATTER_DELIMITER = "---"
_HEADING_PREFIX = "## "


def load_knowledge_base(directory: Path) -> list[KnowledgeChunk]:
    chunks: list[KnowledgeChunk] = []
    for file_path in sorted(directory.glob("*.md")):
        chunks.extend(_load_file(file_path))
    return chunks


def _load_file(file_path: Path) -> list[KnowledgeChunk]:
    metadata, body = _split_frontmatter(file_path.read_text(encoding="utf-8"))
    return [
        KnowledgeChunk(
            text=section_text.strip(),
            heading=heading,
            category=str(metadata.get("category", "")),
            language=str(metadata.get("language", "")),
            last_updated=str(metadata.get("last_updated", "")),
            source_file=file_path.name,
        )
        for heading, section_text in _split_sections(body)
    ]


def _split_frontmatter(raw: str) -> tuple[dict, str]:
    if not raw.startswith(_FRONTMATTER_DELIMITER):
        return {}, raw
    _, frontmatter, body = raw.split(_FRONTMATTER_DELIMITER, 2)
    return yaml.safe_load(frontmatter) or {}, body


def _split_sections(body: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    heading = ""
    lines: list[str] = []
    for line in body.splitlines():
        if line.startswith(_HEADING_PREFIX):
            if heading and lines:
                sections.append((heading, "\n".join(lines)))
            heading = line[len(_HEADING_PREFIX):].strip()
            lines = []
        elif heading:
            lines.append(line)
    if heading and lines:
        sections.append((heading, "\n".join(lines)))
    return sections
