# Chatbot Platform

Farklı firmalara ticari olarak sunulabilecek, çok kiracılı (multi-tenant) ve çok kanallı
(website chat, WhatsApp, Instagram DM ve ileride Telegram/Messenger/sesli asistan) bir
AI chatbot altyapısı.

Her müşterinin bilgi tabanı (knowledge base) koddan bağımsız yönetilir; chatbot her zaman
güncel bilgiyi referans alır, bilgi değiştiğinde kod değişikliği gerekmez.

Mimari kararlar için [ARCHITECTURE.md](ARCHITECTURE.md), geliştirme planı için
[ROADMAP.md](ROADMAP.md) dosyalarına bakın.

## Kurulum

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -e ".[dev]"
```

## Çalıştırma

```bash
uvicorn chatbot_platform.interface.api.main:app --reload
```

`http://localhost:8000/health` adresi `{"status": "ok"}` dönerse kurulum başarılıdır.

## Test

```bash
pytest
```

## Dağıtım (Railway)

Proje bir `Procfile` içerir, Railway (veya benzeri Nixpacks tabanlı platformlar)
GitHub reposunu bağlayıp otomatik dağıtabilir.

Railway panelinde ayarlanması gereken ortam değişkenleri:

- `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `LLM_PROVIDER` — global AI sağlayıcı anahtarları
- Her firma için WhatsApp/Instagram anahtarları da (tek firma varsa) doğrudan buraya
  eklenebilir: `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_ACCESS_TOKEN`,
  `WHATSAPP_VERIFY_TOKEN`, `INSTAGRAM_IG_USER_ID`, `INSTAGRAM_ACCESS_TOKEN`,
  `INSTAGRAM_VERIFY_TOKEN` — `tenants/{id}/.env` dosyası yoksa bu değerlere
  otomatik geri düşülür.

Not: ChromaDB her açılışta `knowledge/` dosyalarından yeniden oluşturulduğu için
kalıcı disk gerekmez. `conversations.sqlite3` (konuşma geçmişi) kalıcı olmasını
istiyorsanız Railway'de bir volume bağlanmalı; bağlanmazsa her yeniden
başlatmada geçmiş sıfırlanır (v1 için kabul edilebilir bir sınırlama).
