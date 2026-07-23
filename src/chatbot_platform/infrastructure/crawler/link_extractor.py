from urllib.parse import urljoin

from bs4 import BeautifulSoup


def extract_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for anchor in soup.find_all("a", href=True):
        absolute_url = urljoin(base_url, anchor["href"])
        links.append(absolute_url.split("#")[0])
    return links
