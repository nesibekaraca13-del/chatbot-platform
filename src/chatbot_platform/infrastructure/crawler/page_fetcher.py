import httpx

_TIMEOUT_SECONDS = 10
_USER_AGENT = "ChatbotPlatformCrawler/0.1"


def fetch_page(url: str, client: httpx.Client | None = None) -> str:
    owns_client = client is None
    client = client or httpx.Client(timeout=_TIMEOUT_SECONDS, headers={"User-Agent": _USER_AGENT})
    try:
        response = client.get(url, follow_redirects=True)
        response.raise_for_status()
        return response.text
    finally:
        if owns_client:
            client.close()
