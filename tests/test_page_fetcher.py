import httpx
import pytest

from chatbot_platform.infrastructure.crawler.page_fetcher import fetch_page


def test_fetch_page_returns_html_body() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="<html><body>Merhaba</body></html>")

    client = httpx.Client(transport=httpx.MockTransport(handler))

    html = fetch_page("https://example.com", client=client)

    assert "Merhaba" in html


def test_fetch_page_raises_on_http_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    with pytest.raises(httpx.HTTPStatusError):
        fetch_page("https://example.com/missing", client=client)
