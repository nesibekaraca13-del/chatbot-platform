# Changelog

Bu proje [Keep a Changelog](https://keepachangelog.com/) formatını takip eder.

## [Unreleased]
### Added
- Knowledge base dosya formatı: markdown + YAML frontmatter (`category`,
  `language`, `last_updated`) ve `##` başlık bazlı bölümleme.
- Örnek/placeholder knowledge dosyaları: `about.md`, `services.md`, `prices.md`,
  `faq.md`, `contact.md`.
- `KnowledgeChunk` domain varlığı ve markdown dosyalarını `##` başlıklarına göre
  parçalayıp frontmatter metadata'sını taşıyan `markdown_loader`.
- `VectorStore` port'u ve Chroma tabanlı implementasyonu (`ChromaVectorStore`);
  yerel/ücretsiz embedding modeli, upsert ile tekrar yüklemede kart çoğaltmama,
  anonim telemetry kapalı.
- `index_knowledge_base` use case'i: knowledge dosyalarını okuyup vector store'a
  yükler.
- `LLMProvider` port'u ve `ChatMessage` domain varlığı; Claude için
  `ClaudeProvider` implementasyonu (test edilebilirlik için istemci dışarıdan
  enjekte ediliyor).

## [0.1.0] - 2026-07-22
### Added
- Proje iskeleti: Ports & Adapters (Hexagonal) klasör yapısı (domain, application,
  infrastructure, interface, config).
- FastAPI uygulaması + `/health` endpoint.
- Temel test altyapısı (pytest + httpx).
- README.md, ARCHITECTURE.md, ROADMAP.md, CLAUDE.md.
