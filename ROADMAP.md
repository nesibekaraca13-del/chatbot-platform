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
- [ ] 20. Meta (WhatsApp + Instagram) adapter
- [ ] 21. Kanal bazlı conversation eşleme
- [ ] 22. Web sitesine gerçekten gömülebilir widget (CORS + internetten
      erişim + tek satır embed script) — Faz 4'ten sonra ele alınacak,
      kullanıcı ile netleşti (2026-07-24)

## Faz 5 — Multi-tenant Altyapı
- [ ] 23. Tenant config modeli
- [ ] 24. Tenant bazlı knowledge base izolasyonu
- [ ] 25. Webhook → tenant routing

## Faz 6 — Provider Çeşitliliği
- [ ] 26. OpenAI adapter
- [x] 27. Gemini adapter (Claude bakiyesi olmadan test edebilmek için Adım 6
      sonrasında öne çekildi)
- [ ] 28. Tenant bazlı provider seçimi (şimdilik `LLM_PROVIDER` env değişkeni
      ile basit seçim yapılıyor, tenant config'e Faz 5'te bağlanacak)

## Faz 7 — Sonraki Dalga (ayrıca planlanacak)
- [ ] Admin panel genişletme
- [ ] Kullanıcı yönetimi & auth
- [ ] CRM entegrasyonu / lead toplama
- [ ] Analytics
- [ ] Dosya/PDF/görsel okuma
- [ ] Sesli asistan
- [ ] Randevu oluşturma
- [ ] Tool calling / MCP / multi-agent
