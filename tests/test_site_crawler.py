import httpx

from chatbot_platform.infrastructure.crawler.site_crawler import crawl_site

_PAGES = {
    "https://example.com/": (
        '<html><body><a href="/page2">2</a>'
        '<a href="https://external.com/">dış</a></body></html>'
    ),
    "https://example.com/page2": '<html><body><a href="/page3">3</a></body></html>',
    "https://example.com/page3": "<html><body>son sayfa</body></html>",
    "https://example.com/robots.txt": "User-agent: *\nDisallow:\n",
}


def _make_client(pages: dict[str, str]) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if url in pages:
            return httpx.Response(200, text=pages[url])
        return httpx.Response(404)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_crawl_site_follows_internal_links_only() -> None:
    client = _make_client(_PAGES)

    pages = crawl_site("https://example.com/", client=client)

    assert set(pages.keys()) == {
        "https://example.com/",
        "https://example.com/page2",
        "https://example.com/page3",
    }


def test_crawl_site_respects_max_pages() -> None:
    client = _make_client(_PAGES)

    pages = crawl_site("https://example.com/", max_pages=2, client=client)

    assert len(pages) == 2


def test_crawl_site_respects_robots_disallow() -> None:
    pages = dict(_PAGES)
    pages["https://example.com/robots.txt"] = "User-agent: *\nDisallow: /page2\n"
    client = _make_client(pages)

    crawled = crawl_site("https://example.com/", client=client)

    assert "https://example.com/page2" not in crawled
    assert "https://example.com/page3" not in crawled
