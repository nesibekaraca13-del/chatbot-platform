from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from chatbot_platform.interface.api.main import app, get_knowledge_dir


@pytest.fixture()
def knowledge_dir(tmp_path: Path) -> Path:
    (tmp_path / "faq.md").write_text(
        "---\ncategory: faq\nlanguage: tr\nlast_updated: 2026-07-23\n---\n\n"
        "## Soru\n\nCevap\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture(autouse=True)
def _override_dependency(knowledge_dir: Path):
    app.dependency_overrides[get_knowledge_dir] = lambda: knowledge_dir
    yield
    app.dependency_overrides.clear()


client = TestClient(app)


def test_list_knowledge_returns_summaries() -> None:
    response = client.get("/knowledge")

    assert response.status_code == 200
    body = response.json()
    assert body == [
        {
            "filename": "faq.md",
            "category": "faq",
            "language": "tr",
            "last_updated": "2026-07-23",
            "heading_count": 1,
        }
    ]


def test_get_knowledge_file_returns_content() -> None:
    response = client.get("/knowledge/faq.md")

    assert response.status_code == 200
    assert "## Soru" in response.json()["content"]


def test_get_knowledge_file_returns_404_when_missing() -> None:
    response = client.get("/knowledge/yok.md")

    assert response.status_code == 404


def test_get_knowledge_file_rejects_path_traversal() -> None:
    response = client.get("/knowledge/..%2Fsecret.md")

    assert response.status_code in (400, 404)
