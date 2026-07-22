# CLAUDE.md

Bu dosya, bu repoda çalışırken Claude Code'un uyması gereken kuralları içerir.

## Süreç (her adım için zorunlu)

1. Problemi analiz et.
2. Alternatif çözümleri değerlendir.
3. Seçilen çözümü ve nedenini açıkla.
4. Gerekirse mimari diyagram oluştur.
5. Yazılacak/değiştirilecek dosyaları listele.
6. Kullanıcıdan onay al.
7. Onaydan sonra kodu yaz.

Onay alınmadan kod yazma. Büyük değişiklikleri tek seferde yapma — ROADMAP.md'deki
adımları tek tek, sırayla uygula.

## Mimari Kurallar

- Ports & Adapters (Hexagonal) mimarisine uy: `domain/` katmanı asla
  `infrastructure/`'ı import etmez.
- Yeni bir AI sağlayıcı, kanal veya veri deposu eklerken önce ilgili port (interface)
  var mı kontrol et; yoksa önce onu tanımla.
- Detaylı mimari kararlar için ARCHITECTURE.md'ye bak, değişiklik yaptığında orayı da
  güncelle.

## Kod Prensipleri

- SOLID, DDD-lite. Gereksiz soyutlama ekleme (YAGNI) — sadece o an gereken minimum
  kodu yaz.
- Yorum yazma, yalnızca "neden" açık olmayan durumlarda kısa bir satır ekle.
- Mevcut sistemi bozmadan yeni özellik ekle; her adım bağımsız test edilebilir ve
  geri alınabilir olmalı.
- Ağır framework'lerden kaçın (örn. LangChain) — ince, kendi yazdığımız port
  arayüzlerini tercih et.

## Bilgi Yönetimi

- Bilgiler asla kod içine gömülmez; `knowledge/` altındaki markdown dosyalarında
  tutulur.
- Promptlar `prompts/` altında ayrı dosyalarda tutulur, koddan ayrıştırılır.

## Değişiklik Kaydı

Her tamamlanan adımda CHANGELOG.md'yi güncelle ve ROADMAP.md'de ilgili maddeyi
işaretle.
