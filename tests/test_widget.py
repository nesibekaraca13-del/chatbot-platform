from fastapi.testclient import TestClient

from chatbot_platform.interface.api.main import app

client = TestClient(app)


def test_widget_is_served() -> None:
    response = client.get("/static/widget.html")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_admin_page_is_served() -> None:
    response = client.get("/static/admin.html")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_embed_script_is_served() -> None:
    response = client.get("/static/embed.js")

    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]
