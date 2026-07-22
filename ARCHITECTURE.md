# Mimari Kararlar

## Genel Yaklaşım

Ports & Adapters (Hexagonal Architecture) + hafif Domain-Driven Design. Amaç: iş
kuralları (domain) hiçbir dış sisteme (AI sağlayıcı, vector DB, mesajlaşma kanalı)
bağımlı olmasın; dış sistemler "adapter" olarak takılıp çıkarılabilsin.

## Katmanlar

- **domain/**: Entity'ler (Tenant, Conversation, Message, KnowledgeChunk) ve port'lar
  (arayüzler: LLMProvider, VectorStore, ChannelSender, KnowledgeRepository). Hiçbir
  infrastructure import'u yapmaz.
- **application/**: Use case'ler (AnswerQuestion, IngestWebsite, UpdateKnowledge).
  Domain port'larını kullanır, somut implementasyonları bilmez.
- **infrastructure/**: Port'ların somut implementasyonları (ChromaDB, Claude/OpenAI/
  Gemini client'ları, SQLite repository'leri, WhatsApp/Instagram API client'ları).
- **interface/**: Dış dünyaya açılan uçlar (FastAPI router'ları, webhook endpoint'leri).
- **config/**: Tenant bazlı konfigürasyon okuma.

## Neden bu yapı?

- **AI sağlayıcı değiştirilebilir olmalı** → `LLMProvider` port'u sayesinde yeni bir
  sağlayıcı eklemek = yeni bir adapter yazmak, domain/application katmanına dokunmadan.
- **Knowledge base bağımsız olmalı** → Bilgiler `knowledge/` altında markdown dosyaları
  olarak tutulur, koda hiç girmez. `VectorStore` port'u üzerinden indexlenir.
- **Yeni kanal eklerken mevcut sistem bozulmamalı** → Kanallar `ChannelSender` port'unun
  birer adapter'ı. Conversation Engine kanaldan habersiz çalışır.
- **Multi-tenant'a geçiş refactor olmamalı** → `tenant_id` kavramı baştan domain
  modelinde var; v1'de tek tenant aktif, v2'de config ile çoğaltılır.

## Knowledge Base Tasarımı

- Markdown dosyaları + YAML frontmatter (kategori, dil, güncellenme tarihi).
- Başlık (`##`) bazlı chunking.
- `knowledge/` klasörü git ile versiyonlanır → audit-trail bedava gelir.
- Değişiklik sonrası re-index tetiklenir (detaylar ROADMAP.md Faz 2-3'te).

## Kanal Soyutlaması

WhatsApp ve Instagram DM ikisi de Meta Graph API üzerinden çalıştığı için ortak bir
temel adapter + kanala özgü ince farklar şeklinde tasarlanacak (Faz 4).

## Fallback Davranışı

Sistem prompt'unda: bilgi tabanında olmayan bir soru sorulduğunda halüsinasyon yapmak
yerine "bilmiyorum / insana yönlendiriyorum" davranışı zorunlu kılınır.

## Bilinçli Ertelenen Kararlar

- Multi-tenant veri izolasyonu (SQLite → Postgres + RLS geçişi) Faz 5'te netleşecek.
- Hybrid search (keyword + vector) fiyat gibi kesin bilgiler için ileride
  değerlendirilecek, v1'de saf vector search yeterli.
- LangChain gibi ağır framework'ler bilinçli olarak kullanılmıyor; ince, kendi
  yazdığımız port arayüzleri tercih ediliyor (leaky abstraction ve versiyon kırılması
  riskini azaltmak için).
