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
