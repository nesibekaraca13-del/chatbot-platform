from collections import deque
from urllib.parse import urlparse

import httpx

from chatbot_platform.infrastructure.crawler.link_extractor import extract_links
from chatbot_platform.infrastructure.crawler.page_fetcher import fetch_page
from chatbot_platform.infrastructure.crawler.robots import RobotsChecker

_DEFAULT_MAX_PAGES = 20


def crawl_site(
    start_url: str,
    max_pages: int = _DEFAULT_MAX_PAGES,
    client: httpx.Client | None = None,
) -> dict[str, str]:
    domain = urlparse(start_url).netloc
    robots_checker = RobotsChecker(start_url, client=client)

    visited: set[str] = set()
    queue: deque[str] = deque([start_url])
    pages: dict[str, str] = {}

    while queue and len(pages) < max_pages:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)

        if not robots_checker.is_allowed(url):
            continue

        try:
            html = fetch_page(url, client=client)
        except httpx.HTTPError:
            continue

        pages[url] = html

        for link in extract_links(html, base_url=url):
            if urlparse(link).netloc == domain and link not in visited:
                queue.append(link)

    return pages
