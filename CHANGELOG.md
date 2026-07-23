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
- `answer_question` use case'i: soruyu vector store'da arar, bulunan bilgiyi
  sistem talimatına ekler, LLM'den cevap alır. Halüsinasyon önleme kuralı
  sistem talimatında yer alıyor (geçici, Adım 7'de ayrı şablon dosyasına
  taşınacak).
- `interface/cli/ask.py`: komut satırından soru sorup uçtan uca akışı deneme
  script'i.
- `GeminiProvider` ve `create_llm_provider` fabrikası: `LLM_PROVIDER` ortam
  değişkenine göre Claude/Gemini arasında seçim yapılabiliyor (Faz 6/Adım 26'nın
  öne çekilmiş hali — Claude hesap bakiyesi olmadan uçtan uca akışı test
  edebilmek için).
- Uçtan uca akış gerçek Gemini API'siyle doğrulandı: sistem bilgi tabanında
  olmayan bir soruda uydurma cevap vermek yerine doğru şekilde
  "bilmiyorum" diyor.
- Sistem promptu koddan `prompts/system_prompt.j2` dosyasına taşındı; Jinja2
  tabanlı `render_system_prompt` ile render ediliyor.

## [0.1.0] - 2026-07-22
### Added
- Proje iskeleti: Ports & Adapters (Hexagonal) klasör yapısı (domain, application,
  infrastructure, interface, config).
- FastAPI uygulaması + `/health` endpoint.
- Temel test altyapısı (pytest + httpx).
- README.md, ARCHITECTURE.md, ROADMAP.md, CLAUDE.md.
