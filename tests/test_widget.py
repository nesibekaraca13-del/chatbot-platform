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
