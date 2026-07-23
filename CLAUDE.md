# CLAUDE.md

Bu dosya, bu repoda çalışırken Claude Code'un uyması gereken kuralları içerir.

## Süreç

Kullanıcı teknik değil ve her adımda onay istenmesini istemiyor — bunu tekrar
sormaya gerek yok, bu kural zaten bunu yansıtıyor.

- Rutin adımlarda (ROADMAP'teki bir sonraki maddeyi uygulamak, test yazmak, küçük
  düzeltmeler/hata giderme): kısaca analiz et, ne yaptığını sade dille özetle,
  onay beklemeden doğrudan uygula ve test et.
- Sadece gerçekten önemli veya geri alınması zor kararlarda onay sor: yeni bir
  mimari yaklaşım, veri kaybına yol açabilecek işlemler, ROADMAP kapsamının
  dışına çıkan genişletmeler, önemli bir bağımlılık/yön değişikliği.
- Büyük değişiklikleri tek seferde yapma — ROADMAP.md'deki adımları tek tek,
  sırayla uygula, her birini test et.
- Kullanıcı kod bilmiyor: her adımın sonunda ne yapıldığını kısa ve sade bir
  dille özetle (teknik jargon yerine analoji/örnek kullan).

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
