from chatbot_platform.infrastructure.crawler.link_extractor import extract_links


def test_extract_links_resolves_relative_urls() -> None:
    html = '<html><body><a href="/about">Hakkımızda</a><a href="https://other.com/">dış</a></body></html>'

    links = extract_links(html, base_url="https://example.com/")

    assert "https://example.com/about" in links
    assert "https://other.com/" in links


def test_extract_links_strips_fragment() -> None:
    html = '<a href="/page#section">link</a>'

    links = extract_links(html, base_url="https://example.com/")

    assert links == ["https://example.com/page"]
