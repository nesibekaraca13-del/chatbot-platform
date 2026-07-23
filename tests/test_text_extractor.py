from chatbot_platform.infrastructure.crawler.text_extractor import (
    extract_clean_text,
    extract_title,
)


def test_extract_clean_text_removes_scripts_and_boilerplate() -> None:
    html = """
    <html>
      <head><title>Test Sayfası</title><style>body{color:red}</style></head>
      <body>
        <nav>Ana Sayfa | Hakkımızda</nav>
        <script>console.log('test')</script>
        <main>
          <h1>Hoş Geldiniz</h1>
          <p>Biz kaliteli hizmet sunuyoruz.</p>
        </main>
        <footer>Telif hakkı 2026</footer>
      </body>
    </html>
    """

    text = extract_clean_text(html)

    assert "Hoş Geldiniz" in text
    assert "Biz kaliteli hizmet sunuyoruz." in text
    assert "console.log" not in text
    assert "color:red" not in text
    assert "Ana Sayfa" not in text
    assert "Telif hakkı" not in text


def test_extract_clean_text_removes_blank_lines() -> None:
    html = "<body><p>Satır 1</p>\n\n\n<p>Satır 2</p></body>"

    text = extract_clean_text(html)

    assert text == "Satır 1\nSatır 2"


def test_extract_title_returns_title_tag_content() -> None:
    html = "<html><head><title>Firma Hakkında</title></head><body></body></html>"

    assert extract_title(html) == "Firma Hakkında"


def test_extract_title_returns_empty_string_when_missing() -> None:
    html = "<html><body>İçerik</body></html>"

    assert extract_title(html) == ""
