# Changelog

Bu proje [Keep a Changelog](https://keepachangelog.com/) formatını takip eder.

## [Unreleased]
### Added
- `Chatbotu_Baslat.bat`: proje klasöründe çift tıklanarak sunucuyu başlatan ve
  sohbet/admin ekranlarını tarayıcıda otomatik açan kısayol (Claude Code
  olmadan bağımsız kullanım için).
- `IncomingMessage` domain varlığı ve `ChannelAdapter` port'u: WhatsApp,
  Instagram gibi kanalların ortak sözleşmesi (gelen mesajı ayrıştırma +
  mesaj gönderme).
- `WhatsAppAdapter`: WhatsApp Cloud API webhook formatını ayrıştırıyor
  (metin mesajlarını işliyor, durum bildirimlerini/tanınmayan formatları
  yok sayıyor) ve Graph API üzerinden cevap gönderiyor. Meta'nın herkese
  açık webhook formatına göre sahte verilerle test edildi — gerçek
  hesapla uçtan uca test, kullanıcının Meta Developer/WhatsApp Business
  hesabı kurmasını gerektiriyor (Adım 21'de ele alınacak).
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
- `ConversationRepository` port'u ve SQLite implementasyonu
  (`SqliteConversationRepository`): konuşma geçmişi kalıcı olarak saklanıyor,
  `answer_question` artık geçmişi LLM'e gönderip yeni mesajları kaydediyor
  (gönderilen geçmiş son 20 mesajla sınırlı, veritabanı kaydı tam kalıyor).
- Sistem promptundaki "sadece Bilgi Kaynağı'nı kullan" kuralı netleştirildi:
  bu kısıtlama yalnızca firma bilgisi sorularına uygulanıyor, konuşma
  hafızasını (örn. kullanıcı adını hatırlama) artık engellemiyor — gerçek
  Gemini denemesinde tespit edilip düzeltildi.
- `POST /chat` endpoint'i: FastAPI `Depends` ile bağımlılık enjeksiyonu
  kullanılarak `vector_store`/`llm_provider`/`conversation_repository`'ye
  erişiyor (gerçek API anahtarı gerektirmeden test edilebilir).
  `conversation_id` gönderilmezse otomatik üretiliyor, gönderilirse konuşma
  kaldığı yerden devam ediyor. Gerçek HTTP isteğiyle uçtan uca doğrulandı.
- Test sohbet ekranı (`/static/widget.html`): basit, tek dosyalık HTML/CSS/JS
  arayüzü, gerçek tarayıcıda denendi — mesajlaşma ve konuşma hafızası
  doğrulandı. Faz 1 bu adımla tamamlandı.
- `fetch_page`: tek bir web sayfasının ham HTML içeriğini indiren fonksiyon
  (`httpx` tabanlı, test edilebilirlik için istemci dışarıdan enjekte
  edilebiliyor). Gerçek bir web adresiyle (`example.com`) doğrulandı.
- `crawl_site`: bir başlangıç adresinden aynı domain içindeki linkleri takip
  ederek çoklu sayfa indirme (varsayılan en fazla 20 sayfa). `RobotsChecker`
  ile robots.txt kurallarına uyuyor (robots.txt yoksa taramaya izin
  veriliyor). Link bulma için `BeautifulSoup` eklendi. Gerçek bir sitede
  (python.org) doğrulandı.
- `extract_clean_text` ve `extract_title`: ham HTML'den script/stil/menü/
  altbilgi gibi gürültüyü çıkarıp okunabilir metin ve sayfa başlığı elde
  ediyor. Gerçek bir sayfada (python.org/about) doğrulandı.
- `generate_draft_knowledge_files`: taranan sayfaları, mevcut knowledge
  formatına (frontmatter + `##` başlık) uygun taslak `.md` dosyalarına
  dönüştürüyor; her taslakta kaynak adresi (`source_url`) bulunuyor. Üretilen
  taslakların `markdown_loader` ile de doğru okunduğu test edildi. Gerçek bir
  siteyle (python.org) uçtan uca doğrulandı.
- `approve_draft_knowledge` use case'i ve `crawl`/`approve` CLI komutları:
  tarama → taslak üretme → gözden geçirme → onaylanan dosyaları `knowledge/`
  klasörüne taşıma → otomatik yeniden indexleme akışı tamamlandı. Gerçek bir
  siteyle uçtan uca doğrulandı. Faz 2 (otomatik içerik alma) bu adımla
  tamamlandı.
- `GET /knowledge` ve `GET /knowledge/{filename}` endpoint'leri: knowledge
  dosyalarının özetini (kategori, dil, son güncelleme, başlık sayısı) ve tek
  bir dosyanın tam içeriğini döndürüyor. Dosya adı doğrulaması (path
  traversal koruması) dahil. Gerçek proje verisiyle doğrulandı.
- `PUT /knowledge/{filename}` ve `DELETE /knowledge/{filename}` endpoint'leri:
  dosya oluşturma/güncelleme/silme, ardından otomatik yeniden indexleme.
- **Düzeltme:** `VectorStore`'a `clear()` eklendi; `index_knowledge_base`
  artık önce hafızayı temizleyip sonra yeniden yüklüyor. Önceden sadece
  upsert yapıldığı için silinen dosyaların bilgi kartları hafızada
  (ChromaDB) kalıyordu — artık silme işlemi hem dosyayı hem hafızadaki
  kaydı temizliyor. Gerçek ChromaDB ile uçtan uca doğrulandı.
- Minimal admin arayüzü (`/static/admin.html`): knowledge dosyalarını listeleme,
  görüntüleme, düzenleyip kaydetme, silme ve yeni dosya oluşturma. Gerçek
  tarayıcıda denendi (oluşturma + silme uçtan uca doğrulandı). Faz 3 (bilgi
  yönetimi) bu adımla tamamlandı.

## [0.1.0] - 2026-07-22
### Added
- Proje iskeleti: Ports & Adapters (Hexagonal) klasör yapısı (domain, application,
  infrastructure, interface, config).
- FastAPI uygulaması + `/health` endpoint.
- Temel test altyapısı (pytest + httpx).
- README.md, ARCHITECTURE.md, ROADMAP.md, CLAUDE.md.
