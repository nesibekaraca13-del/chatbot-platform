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

- Hybrid search (keyword + vector) fiyat gibi kesin bilgiler için ileride
  değerlendirilecek, v1'de saf vector search yeterli.
- LangChain gibi ağır framework'ler bilinçli olarak kullanılmıyor; ince, kendi
  yazdığımız port arayüzleri tercih ediliyor (leaky abstraction ve versiyon kırılması
  riskini azaltmak için).

## Multi-Tenant Mimarisi (Faz 5)

- Her firma `tenants/{tenant_id}/` altında kendi klasörüne sahip: `config.yaml`
  (isim, tercih edilen AI sağlayıcısı — sır içermez, git'e girer) + `knowledge/`
  (o firmanın bilgi dosyaları) + opsiyonel `.env` (WhatsApp/Instagram anahtarları
  gibi sırlar — git'e girmez, `.gitignore`'da `tenants/*/.env`).
- **Vector store izolasyonu**: Tüm firmalar aynı `chroma_db/` klasörünü paylaşır
  ama her firmanın kendi Chroma koleksiyonu vardır (`knowledge_{tenant_id}`) —
  ayrı bir veritabanı dizinine gerek yok, Chroma'nın koleksiyon izolasyonu yeterli.
- **Konuşma izolasyonu**: Tek bir SQLite dosyası paylaşılır; `conversation_id`
  her zaman `{tenant_id}:...` ile başlar, bu da doğal bir bölümleme sağlar —
  ayrı bir veritabanı dosyasına gerek yok.
- **API/webhook routing**: Uç noktalar `/t/{tenant_id}/...` şeklinde firma bazlı.
  WhatsApp/Instagram webhook URL'leri Meta'ya firma başına ayrı ayrı verilir
  (`.../t/{tenant_id}/webhook/whatsapp`). Web sitesi widget'ı (`embed.js`)
  `data-tenant` özniteliğinden hangi firmaya ait olduğunu okur.
- **API anahtarları global, sağlayıcı seçimi firma bazlı**: Anthropic/Gemini API
  anahtarları tüm platform için tek (kök `.env`), ama her firma `config.yaml`
  üzerinden Claude veya Gemini'den birini seçebilir. WhatsApp/Instagram
  anahtarları ise gerçekten firma bazlı (her firmanın kendi hesabı olduğu için).
  uygulama başlangıcında (lifespan) her firma için knowledge base indexlenir ve
  gerekli adapter'lar kurulur; yeni firma eklemek/config değiştirmek için
  sunucunun yeniden başlatılması gerekir (v1 için kabul edilebilir, hot-reload
  şimdilik hedeflenmiyor).
