# Roadmap

Her adım şu sırayla ilerler: analiz → alternatif değerlendirme → karar gerekçesi →
(gerekirse diyagram) → dosya listesi → onay → kod. Her adım test edilebilir ve geri
alınabilir olmalı.

## Faz 1 — Tek Kanal, Tek Tenant, Lokal Çekirdek
- [x] 1. Proje iskeleti
- [x] 2. Knowledge base dosya formatı + örnek içerik
- [x] 3. Markdown loader + chunker
- [x] 4. ChromaDB embedding/indexleme pipeline
- [x] 5. LLMProvider interface + Claude implementasyonu
- [x] 6. RAG cevap akışı (CLI testi)
- [x] 7. Sistem prompt şablonu (Jinja2) + fallback kuralı
- [x] 8. Konuşma geçmişi + loglama (SQLite)
- [x] 9. FastAPI /chat endpoint
- [x] 10. Test chat widget

## Faz 2 — Otomatik İçerik Alma
- [x] 11. Tek sayfa web crawler
- [x] 12. Çoklu sayfa crawling (robots.txt uyumlu)
- [x] 13. HTML → temiz metin extraction
- [x] 14. Draft knowledge dosyası üretimi
- [x] 15. Review & approve akışı → commit + re-index

## Faz 3 — Bilgi Yönetimi
- [x] 16. Knowledge listeleme/görüntüleme API
- [x] 17. Ekle/güncelle/sil API + otomatik re-index
- [x] 18. Minimal admin arayüzü

## Faz 4 — Çoklu Kanal
- [x] 19. Channel adapter interface
- [x] 20a. WhatsApp adapter
- [x] 20b. Instagram DM adapter
- [x] 21. Kanal bazlı conversation eşleme (webhook endpoint'leri + kod
      tarafı tamamlandı; gerçek Meta hesabıyla uçtan uca test kullanıcının
      Meta Developer hesabı kurmasını ve genel erişilebilir bir adres
      gerektiriyor — Adım 22 ile birlikte ele alınacak)
- [x] 22. Web sitesine gerçekten gömülebilir widget (`embed.js` + iframe
      tabanlı yerleştirme, ngrok tüneliyle farklı bir origin'den uçtan uca
      test edildi)

## Faz 5 — Multi-tenant Altyapı
- [x] 23. Tenant config modeli
- [x] 24. Tenant bazlı knowledge base izolasyonu
- [x] 25. Webhook → tenant routing

## Faz 6 — Provider Çeşitliliği
- [ ] 26. OpenAI adapter
- [x] 27. Gemini adapter (Claude bakiyesi olmadan test edebilmek için Adım 6
      sonrasında öne çekildi)
- [ ] 28. Tenant bazlı provider seçimi (şimdilik `LLM_PROVIDER` env değişkeni
      ile basit seçim yapılıyor, tenant config'e Faz 5'te bağlanacak)

## Faz 8 — Canlı Yayına Geçiş (Railway + Meta Onayı)
- [x] 29. Railway'de canlı barındırma (Railpack build sorunları çözüldü:
      `requirements.txt`, `PYTHONPATH=src`). Sunucu 7/24 ayakta,
      `/health` ve WhatsApp webhook uçtan uca doğrulandı.
- [ ] 30. Meta App Review + Business Verification. Uygulama yayınlanmadan
      gerçek WhatsApp kullanıcılarından gelen mesajlar webhook'a otomatik
      iletilmiyor (sadece Meta panelindeki "Test" butonu iletiliyor).
      Bu onaylanana kadar gerçek mesajlar elle simüle ediliyor. Bu adım
      her yeni firma/tenant kendi WhatsApp numarasını bağladığında da
      tekrarlanacak standart bir Meta gereksinimi.
- [ ] 31. Kalıcı (süresi dolmayan) WhatsApp erişim token'ı — Business
      Verification sonrası bir System User oluşturup kalıcı token
      üretilecek; şu an geçici test token'ları ~24 saatte bir manuel
      yenileniyor.

## Faz 7 — Sonraki Dalga (ayrıca planlanacak)
- [ ] Admin panel genişletme
- [ ] Kullanıcı yönetimi & auth
- [ ] CRM entegrasyonu / lead toplama
- [ ] Analytics
- [ ] Dosya/PDF/görsel okuma
- [ ] Sesli asistan
- [ ] Randevu oluşturma
- [ ] Tool calling / MCP / multi-agent
