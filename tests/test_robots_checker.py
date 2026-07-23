import httpx

from chatbot_platform.infrastructure.crawler.robots import RobotsChecker


def test_disallowed_path_is_blocked() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="User-agent: *\nDisallow: /private\n")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    checker = RobotsChecker("https://example.com/", client=client)

    assert checker.is_allowed("https://example.com/private/page") is False
    assert checker.is_allowed("https://example.com/public") is True


def test_missing_robots_txt_allows_everything() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    checker = RobotsChecker("https://example.com/", client=client)

    assert checker.is_allowed("https://example.com/anything") is True
