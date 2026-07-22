# Roadmap

Her adım şu sırayla ilerler: analiz → alternatif değerlendirme → karar gerekçesi →
(gerekirse diyagram) → dosya listesi → onay → kod. Her adım test edilebilir ve geri
alınabilir olmalı.

## Faz 1 — Tek Kanal, Tek Tenant, Lokal Çekirdek
- [x] 1. Proje iskeleti
- [x] 2. Knowledge base dosya formatı + örnek içerik
- [ ] 3. Markdown loader + chunker
- [ ] 4. ChromaDB embedding/indexleme pipeline
- [ ] 5. LLMProvider interface + Claude implementasyonu
- [ ] 6. RAG cevap akışı (CLI testi)
- [ ] 7. Sistem prompt şablonu (Jinja2) + fallback kuralı
- [ ] 8. Konuşma geçmişi + loglama (SQLite)
- [ ] 9. FastAPI /chat endpoint
- [ ] 10. Test chat widget

## Faz 2 — Otomatik İçerik Alma
- [ ] 11. Tek sayfa web crawler
- [ ] 12. Çoklu sayfa crawling (robots.txt uyumlu)
- [ ] 13. HTML → temiz metin extraction
- [ ] 14. Draft knowledge dosyası üretimi
- [ ] 15. Review & approve akışı → commit + re-index

## Faz 3 — Bilgi Yönetimi
- [ ] 16. Knowledge listeleme/görüntüleme API
- [ ] 17. Ekle/güncelle/sil API + otomatik re-index
- [ ] 18. Minimal admin arayüzü

## Faz 4 — Çoklu Kanal
- [ ] 19. Channel adapter interface
- [ ] 20. Meta (WhatsApp + Instagram) adapter
- [ ] 21. Kanal bazlı conversation eşleme

## Faz 5 — Multi-tenant Altyapı
- [ ] 22. Tenant config modeli
- [ ] 23. Tenant bazlı knowledge base izolasyonu
- [ ] 24. Webhook → tenant routing

## Faz 6 — Provider Çeşitliliği
- [ ] 25. OpenAI adapter
- [ ] 26. Gemini adapter
- [ ] 27. Tenant bazlı provider seçimi

## Faz 7 — Sonraki Dalga (ayrıca planlanacak)
- [ ] Admin panel genişletme
- [ ] Kullanıcı yönetimi & auth
- [ ] CRM entegrasyonu / lead toplama
- [ ] Analytics
- [ ] Dosya/PDF/görsel okuma
- [ ] Sesli asistan
- [ ] Randevu oluşturma
- [ ] Tool calling / MCP / multi-agent
