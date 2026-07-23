import urllib.robotparser
from urllib.parse import urlparse

import httpx

from chatbot_platform.infrastructure.crawler.page_fetcher import fetch_page

_USER_AGENT = "ChatbotPlatformCrawler/0.1"


class RobotsChecker:
    def __init__(self, start_url: str, client: httpx.Client | None = None) -> None:
        parsed = urlparse(start_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

        self._parser = urllib.robotparser.RobotFileParser()
        try:
            robots_txt = fetch_page(robots_url, client=client)
            self._parser.parse(robots_txt.splitlines())
        except httpx.HTTPError:
            self._parser.allow_all = True

    def is_allowed(self, url: str) -> bool:
        return self._parser.can_fetch(_USER_AGENT, url)
