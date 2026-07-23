from bs4 import BeautifulSoup

_TAGS_TO_REMOVE = ["script", "style", "nav", "header", "footer", "aside", "noscript"]


def extract_clean_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag_name in _TAGS_TO_REMOVE:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    text = soup.get_text(separator="\n")
    non_empty_lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(non_empty_lines)


def extract_title(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    return ""
